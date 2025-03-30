#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
워드프레스 블로그 게시 모듈 (REST API 사용)
"""

import os
import sys
import json
import datetime
import re
from PIL import Image
import requests
import frontmatter
import markdown2
from io import BytesIO
from dotenv import load_dotenv
from base64 import b64encode
from urllib.parse import urljoin

# 환경 변수 로드
load_dotenv()

class WordPressPublisher:
    """생성된 블로그를 워드프레스에 게시하는 클래스"""
    
    def __init__(self):
        """초기화 함수"""
        # 워드프레스 설정
        self.wp_url = os.getenv('WP_URL')
        self.wp_username = os.getenv('WP_USERNAME')
        self.wp_password = os.getenv('WP_APP_PASSWORD')
        
        # REST API 엔드포인트
        self.api_url = urljoin(self.wp_url, 'wp-json/wp/v2')
        self.auth_token = None
        
        # 입출력 디렉토리 설정
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'output')
        self.images_dir = os.path.join(self.output_dir, 'images')
        self.metadata_dir = os.path.join(self.output_dir, 'metadata')
        self.blogs_dir = os.path.join(self.output_dir, 'blogs')
        
        # 디렉토리 생성
        for directory in [self.output_dir, self.images_dir, self.metadata_dir, self.blogs_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def find_latest_blog(self):
        """가장 최근에 생성된 블로그 파일을 찾습니다.
        
        Returns:
            str: 블로그 파일 경로 또는 None
        """
        try:
            if not os.path.exists(self.blogs_dir):
                print("블로그 디렉토리를 찾을 수 없습니다.")
                return None
            
            # .md 파일만 필터링
            blog_files = [f for f in os.listdir(self.blogs_dir) if f.endswith('.md')]
            if not blog_files:
                print("발행할 블로그 포스트를 찾을 수 없습니다.")
                return None
            
            # 최신 파일 찾기
            latest_file = max(blog_files, key=lambda x: os.path.getctime(os.path.join(self.blogs_dir, x)))
            return os.path.join(self.blogs_dir, latest_file)
            
        except Exception as e:
            print(f"블로그 파일 검색 중 오류 발생: {str(e)}")
            return None

    def process_blog_content(self, file_path):
        """블로그 파일의 내용을 처리합니다.
        
        Args:
            file_path (str): 블로그 파일 경로
            
        Returns:
            tuple: (제목, 내용, 메타데이터)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # 메타데이터 추출
            metadata = post.metadata
            title = metadata.get('title', '')
            
            # Markdown을 HTML로 변환
            content = markdown2.markdown(post.content, extras=['fenced-code-blocks', 'tables'])
            
            return title, content, metadata
            
        except Exception as e:
            print(f"블로그 내용 처리 중 오류 발생: {str(e)}")
            return None, None, None

    def find_blog_images(self, content):
        """블로그 내용에서 이미지 파일을 찾습니다.
        
        Args:
            content (str): 블로그 내용
            
        Returns:
            list: 이미지 파일 경로 리스트
        """
        try:
            # 이미지 디렉토리의 모든 이미지 파일
            image_files = []
            if os.path.exists(self.images_dir):
                image_files = [os.path.join(self.images_dir, f) for f in os.listdir(self.images_dir)
                             if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
            return image_files
            
        except Exception as e:
            print(f"이미지 파일 검색 중 오류 발생: {str(e)}")
            return []

    def optimize_image(self, image_path):
        """이미지를 최적화합니다.
        
        Args:
            image_path (str): 원본 이미지 파일 경로
            
        Returns:
            str: 최적화된 이미지 파일 경로
        """
        try:
            # 이미지 로드
            with Image.open(image_path) as img:
                # 이미지가 너무 크면 리사이즈
                max_size = (1920, 1080)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.LANCZOS)
                
                # 최적화된 이미지 저장
                optimized_path = image_path.replace('.', '_optimized.')
                img.save(optimized_path, optimize=True, quality=85)
                
                return optimized_path
                
        except Exception as e:
            print(f"이미지 최적화 중 오류 발생: {str(e)}")
            return image_path

    def connect_to_wordpress(self):
        """워드프레스에 연결 및 인증
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            if not all([self.wp_url, self.wp_username, self.wp_password]):
                print("워드프레스 연결 정보가 설정되지 않았습니다. .env 파일을 확인하세요.")
                return False
            
            # Basic Auth 토큰 생성
            credentials = f"{self.wp_username}:{self.wp_password}"
            self.auth_token = b64encode(credentials.encode()).decode()
            
            # 연결 테스트
            headers = {
                'Authorization': f'Basic {self.auth_token}'
            }
            response = requests.get(f"{self.api_url}/users/me", headers=headers)
            
            if response.status_code == 200:
                print("워드프레스에 연결되었습니다.")
                return True
            else:
                print(f"워드프레스 연결 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                self.auth_token = None
                return False
                
        except Exception as e:
            print(f"워드프레스 연결 중 오류 발생: {str(e)}")
            self.auth_token = None
            return False

    def test_connection(self):
        """워드프레스 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            if not self.auth_token:
                return self.connect_to_wordpress()
            
            headers = {
                'Authorization': f'Basic {self.auth_token}'
            }
            response = requests.get(f"{self.api_url}/users/me", headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"워드프레스에 연결되었습니다. 사용자: {user_info['name']}")
                return True
            else:
                print(f"워드프레스 연결 테스트 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"워드프레스 연결 테스트 중 오류 발생: {str(e)}")
            return False

    def upload_image_to_wordpress(self, image_path, title=None, alt_text=None, caption=None):
        """워드프레스에 이미지 업로드
        
        Args:
            image_path (str): 업로드할 이미지 파일 경로
            title (str, optional): 이미지 제목
            alt_text (str, optional): 대체 텍스트
            caption (str, optional): 이미지 캡션
            
        Returns:
            dict: 업로드된 이미지 정보 (URL 등)
        """
        try:
            if not self.auth_token:
                if not self.connect_to_wordpress():
                    return None
            
            # 이미지 최적화
            optimized_path = self.optimize_image(image_path)
            
            # 이미지 데이터 준비
            headers = {
                'Authorization': f'Basic {self.auth_token}',
                'Content-Disposition': f'attachment; filename={os.path.basename(optimized_path)}'
            }
            
            with open(optimized_path, 'rb') as img:
                files = {
                    'file': img
                }
                
                response = requests.post(
                    f"{self.api_url}/media",
                    headers=headers,
                    files=files
                )
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                # 이미지 메타데이터 업데이트
                if title or alt_text or caption:
                    meta = {}
                    if title:
                        meta['title'] = title
                    if alt_text:
                        meta['alt_text'] = alt_text
                    if caption:
                        meta['caption'] = caption
                    
                    update_response = requests.post(
                        f"{self.api_url}/media/{data['id']}",
                        headers={
                            'Authorization': f'Basic {self.auth_token}',
                            'Content-Type': 'application/json'
                        },
                        json=meta
                    )
                    
                    if update_response.status_code in [200, 201]:
                        data = update_response.json()
                
                print(f"이미지가 워드프레스에 업로드되었습니다. URL: {data['source_url']}")
                return {
                    'id': data['id'],
                    'url': data['source_url'],
                    'title': data['title']['rendered'],
                    'alt_text': data.get('alt_text', ''),
                    'caption': data.get('caption', {}).get('rendered', '')
                }
            else:
                print(f"이미지 업로드 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return None
                
        except Exception as e:
            print(f"이미지 업로드 중 오류 발생: {str(e)}")
            return None

    def publish_blog(self, title, content, metadata=None, images=None, publish=True):
        """블로그 게시
        
        Args:
            title (str): 블로그 제목
            content (str): 블로그 내용
            metadata (dict, optional): 블로그 메타데이터
            images (list, optional): 이미지 파일 경로 리스트
            publish (bool, optional): 즉시 게시 여부. 기본값은 True.
            
        Returns:
            str: 게시된 포스트 URL
        """
        try:
            if not self.auth_token:
                if not self.connect_to_wordpress():
                    return None
            
            # 이미지 업로드 및 URL 치환
            if images:
                for image_path in images:
                    image_info = self.upload_image_to_wordpress(
                        image_path,
                        title=os.path.basename(image_path),
                        alt_text=os.path.basename(image_path)
                    )
                    if image_info:
                        # 이미지 URL을 콘텐츠에 추가
                        content += f"\n\n<img src='{image_info['url']}' alt='{image_info['alt_text']}' />"
            
            # 포스트 데이터 준비
            post_data = {
                'title': title,
                'content': content,
                'status': 'publish' if publish else 'draft'
            }
            
            # 메타데이터 처리
            if metadata:
                if 'categories' in metadata:
                    post_data['categories'] = self.get_category_ids(metadata['categories'])
                if 'tags' in metadata:
                    post_data['tags'] = self.get_tag_ids(metadata['tags'])
            
            # 포스트 생성
            headers = {
                'Authorization': f'Basic {self.auth_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/posts",
                headers=headers,
                json=post_data
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"블로그가 성공적으로 게시되었습니다. URL: {data['link']}")
                return data['link']
            else:
                print(f"블로그 게시 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return None
                
        except Exception as e:
            print(f"블로그 게시 중 오류 발생: {str(e)}")
            return None

    def get_category_ids(self, categories):
        """카테고리 이름을 ID로 변환
        
        Args:
            categories (list): 카테고리 이름 리스트
            
        Returns:
            list: 카테고리 ID 리스트
        """
        try:
            headers = {
                'Authorization': f'Basic {self.auth_token}'
            }
            
            category_ids = []
            for category in categories:
                # 카테고리 검색
                response = requests.get(
                    f"{self.api_url}/categories",
                    headers=headers,
                    params={'search': category}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        category_ids.append(data[0]['id'])
                    else:
                        # 카테고리가 없으면 생성
                        create_response = requests.post(
                            f"{self.api_url}/categories",
                            headers={**headers, 'Content-Type': 'application/json'},
                            json={'name': category}
                        )
                        if create_response.status_code in [200, 201]:
                            category_ids.append(create_response.json()['id'])
            
            return category_ids
            
        except Exception as e:
            print(f"카테고리 ID 변환 중 오류 발생: {str(e)}")
            return []

    def get_tag_ids(self, tags):
        """태그 이름을 ID로 변환
        
        Args:
            tags (list): 태그 이름 리스트
            
        Returns:
            list: 태그 ID 리스트
        """
        try:
            headers = {
                'Authorization': f'Basic {self.auth_token}'
            }
            
            tag_ids = []
            for tag in tags:
                # 태그 검색
                response = requests.get(
                    f"{self.api_url}/tags",
                    headers=headers,
                    params={'search': tag}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        tag_ids.append(data[0]['id'])
                    else:
                        # 태그가 없으면 생성
                        create_response = requests.post(
                            f"{self.api_url}/tags",
                            headers={**headers, 'Content-Type': 'application/json'},
                            json={'name': tag}
                        )
                        if create_response.status_code in [200, 201]:
                            tag_ids.append(create_response.json()['id'])
            
            return tag_ids
            
        except Exception as e:
            print(f"태그 ID 변환 중 오류 발생: {str(e)}")
            return []

def main():
    """메인 실행 함수"""
    try:
        publisher = WordPressPublisher()
        
        # 워드프레스 연결 테스트
        if not publisher.test_connection():
            print("워드프레스 연결에 실패했습니다.")
            return
        
        # 최신 블로그 파일 찾기
        blog_file = publisher.find_latest_blog()
        if not blog_file:
            print("처리할 블로그 내용이 없습니다.")
            return
        
        # 블로그 내용 처리
        title, content, metadata = publisher.process_blog_content(blog_file)
        if not title or not content:
            print("블로그 내용을 처리할 수 없습니다.")
            return
        
        # 이미지 파일 찾기
        images = publisher.find_blog_images(content)
        
        # 블로그 게시
        post_url = publisher.publish_blog(title, content, metadata, images)
        if post_url:
            print(f"블로그가 성공적으로 게시되었습니다: {post_url}")
        else:
            print("블로그 게시에 실패했습니다.")
            
    except Exception as e:
        print(f"실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 