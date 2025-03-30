#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
워드프레스 블로그 게시 모듈
"""

import os
import sys
import json
import datetime
import re
from PIL import Image
import requests
from io import BytesIO
from dotenv import load_dotenv
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPosts
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.compat import xmlrpc_client

# 환경 변수 로드
load_dotenv()

class WordPressPublisher:
    """생성된 블로그를 워드프레스에 게시하는 클래스"""
    
    def __init__(self):
        """초기화 함수"""
        # 워드프레스 설정
        self.wp_url = os.getenv('WP_URL')
        self.wp_username = os.getenv('WP_USERNAME')
        self.wp_password = os.getenv('WP_PASSWORD')
        
        # 입출력 디렉토리 설정
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        self.images_dir = os.path.join(self.output_dir, 'images')
        self.metadata_dir = os.path.join(self.output_dir, 'metadata')
        
        # 디렉토리 생성
        for directory in [self.output_dir, self.images_dir, self.metadata_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # 워드프레스 클라이언트
        self.client = None
    
    def connect_to_wordpress(self):
        """워드프레스에 연결
        
        Returns:
            Client: 워드프레스 클라이언트 객체
        """
        try:
            if not all([self.wp_url, self.wp_username, self.wp_password]):
                print("워드프레스 연결 정보가 설정되지 않았습니다. .env 파일을 확인하세요.")
                return None
            
            self.client = Client(self.wp_url, self.wp_username, self.wp_password)
            return self.client
        except Exception as e:
            print(f"워드프레스 연결 중 오류 발생: {e}")
            return None

    def optimize_image(self, image_path, max_size=(1200, 1200), quality=85):
        """이미지 최적화
        
        Args:
            image_path (str): 최적화할 이미지 파일 경로
            max_size (tuple): 최대 이미지 크기 (width, height)
            quality (int): 이미지 품질 (1-100)
            
        Returns:
            str: 최적화된 이미지 파일 경로
        """
        try:
            # 이미지 로드
            img = Image.open(image_path)
            
            # 이미지 크기 최적화
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 최적화된 이미지 저장
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            optimized_filename = f"{name}_optimized{ext}"
            optimized_path = os.path.join(os.path.dirname(image_path), optimized_filename)
            
            # PNG 파일은 quality 파라미터 무시
            if ext.lower() == '.png':
                img.save(optimized_path, 'PNG', optimize=True)
            else:
                img.save(optimized_path, quality=quality, optimize=True)
            
            print(f"이미지가 최적화되어 {optimized_path}에 저장되었습니다.")
            return optimized_path
            
        except Exception as e:
            print(f"이미지 최적화 중 오류 발생: {e}")
            return image_path

    def save_image_metadata(self, image_path, metadata):
        """이미지 메타데이터 저장
        
        Args:
            image_path (str): 이미지 파일 경로
            metadata (dict): 저장할 메타데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # 메타데이터에 기본 정보 추가
            metadata.update({
                'original_path': image_path,
                'filename': os.path.basename(image_path),
                'created_at': datetime.datetime.now().isoformat(),
            })
            
            # 이미지 정보 추가
            with Image.open(image_path) as img:
                metadata.update({
                    'size': img.size,
                    'format': img.format,
                    'mode': img.mode,
                })
            
            # 메타데이터 파일 경로
            filename = os.path.basename(image_path)
            metadata_filename = f"{os.path.splitext(filename)[0]}_metadata.json"
            metadata_path = os.path.join(self.metadata_dir, metadata_filename)
            
            # 메타데이터 저장
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"메타데이터가 {metadata_path}에 저장되었습니다.")
            return True
            
        except Exception as e:
            print(f"메타데이터 저장 중 오류 발생: {e}")
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
            if self.client is None:
                self.connect_to_wordpress()
            
            if self.client is None:
                raise Exception("워드프레스 클라이언트가 초기화되지 않았습니다.")
            
            # 이미지 최적화
            optimized_path = self.optimize_image(image_path)
            
            # 이미지 데이터 준비
            with open(optimized_path, 'rb') as img:
                filename = os.path.basename(optimized_path)
                data = {
                    'name': filename,
                    'type': f'image/{os.path.splitext(filename)[1][1:]}',
                    'bits': xmlrpc_client.Binary(img.read()),
                    'overwrite': True
                }
                
                # 메타데이터 추가
                if title:
                    data['title'] = title
                if alt_text:
                    data['alt'] = alt_text
                if caption:
                    data['caption'] = caption
            
            # 이미지 업로드
            response = self.client.call(UploadFile(data))
            
            # 메타데이터 저장
            metadata = {
                'wordpress_id': response['id'],
                'url': response['url'],
                'title': title,
                'alt_text': alt_text,
                'caption': caption,
                'upload_date': datetime.datetime.now().isoformat()
            }
            self.save_image_metadata(image_path, metadata)
            
            print(f"이미지가 워드프레스에 업로드되었습니다. URL: {response['url']}")
            return response
            
        except Exception as e:
            print(f"이미지 업로드 중 오류 발생: {e}")
            return None

    def insert_images_to_content(self, content, image_urls):
        """블로그 내용에 이미지 삽입
        
        Args:
            content (str): 블로그 내용
            image_urls (list): 이미지 URL 리스트
            
        Returns:
            str: 이미지가 삽입된 블로그 내용
        """
        try:
            # 이미지 설명 패턴 찾기
            patterns = [
                r'\[이미지 설명 (\d+)\].*?(?=\[이미지 설명 \d+\]|$)',
                r'\[여기에 이미지 (\d+) 삽입\].*?(?=\[여기에 이미지 \d+ 삽입\]|$)'
            ]
            
            modified_content = content
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in matches:
                    idx = int(match.group(1)) - 1
                    if idx < len(image_urls):
                        # 이미지 HTML 태그 생성
                        img_html = f'<img src="{image_urls[idx]}" class="wp-image" alt="AI 뉴스 이미지 {idx + 1}" />'
                        # 이미지 설명을 이미지 태그로 교체
                        modified_content = modified_content.replace(match.group(0), img_html)
            
            return modified_content
            
        except Exception as e:
            print(f"이미지 삽입 중 오류 발생: {e}")
            return content

    def process_images_for_blog(self, content, images):
        """블로그용 이미지 처리 워크플로우
        
        Args:
            content (str): 블로그 내용
            images (list): 이미지 파일 경로 리스트
            
        Returns:
            tuple: (이미지가 삽입된 블로그 내용, 업로드된 이미지 URL 리스트)
        """
        try:
            image_urls = []
            
            # 각 이미지 처리
            for i, image_path in enumerate(images, 1):
                # 이미지 업로드
                response = self.upload_image_to_wordpress(
                    image_path,
                    title=f"AI 뉴스 이미지 {i}",
                    alt_text=f"AI 기술 뉴스 이미지 {i}",
                    caption=f"AI 뉴스 블로그 이미지 {i}"
                )
                
                if response:
                    image_urls.append(response['url'])
            
            # 블로그 내용에 이미지 삽입
            modified_content = self.insert_images_to_content(content, image_urls)
            
            return modified_content, image_urls
            
        except Exception as e:
            print(f"이미지 처리 중 오류 발생: {e}")
            return content, []

    def publish_blog(self, title, content, images=None, client=None, publish=True):
        """블로그 게시
        
        Args:
            title (str): 블로그 제목
            content (str): 블로그 내용
            images (list, optional): 이미지 파일 경로 리스트
            client (Client, optional): 워드프레스 클라이언트 객체
            publish (bool, optional): 즉시 게시 여부. 기본값은 True.
            
        Returns:
            str: 게시된 포스트 ID
        """
        if client is None:
            client = self.connect_to_wordpress()
            
        if client is None:
            print("워드프레스 연결에 실패했습니다.")
            return None
        
        try:
            # 이미지 처리
            if images:
                content, image_urls = self.process_images_for_blog(content, images)
            
            # HTML로 변환
            html_content = self.markdown_to_html(content)
            
            # 포스트 생성
            post = WordPressPost()
            post.title = title
            post.content = html_content
            post.terms_names = {
                'category': ['AI', '기술', '뉴스'],
                'post_tag': ['인공지능', '기술동향', '자동화']
            }
            post.post_status = 'publish' if publish else 'draft'
            
            # 포스트 게시
            post_id = client.call(NewPost(post))
            
            status = "게시" if publish else "임시저장"
            print(f"블로그가 성공적으로 {status}되었습니다. 포스트 ID: {post_id}")
            return post_id
            
        except Exception as e:
            print(f"블로그 게시 중 오류 발생: {e}")
            return None

def main():
    """메인 함수"""
    publisher = WordPressPublisher()
    
    # 블로그 내용 로드
    blog_content = publisher.load_blog_content()
    
    if blog_content:
        # 제목과 본문 추출
        title, content = publisher.extract_title_and_content(blog_content)
        
        if title and content:
            # 이미지 파일 찾기
            images = [f for f in os.listdir(publisher.images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
            image_paths = [os.path.join(publisher.images_dir, f) for f in images]
            
            # 워드프레스 연결 테스트
            client = publisher.connect_to_wordpress()
            
            if client and publisher.test_connection(client):
                # 실제 워드프레스에 게시
                post_id = publisher.publish_blog(title, content, image_paths, client)
                if post_id:
                    print(f"블로그가 워드프레스에 성공적으로 게시되었습니다. 포스트 ID: {post_id}")
            else:
                # 연결 실패 시 시뮬레이션 실행
                print("워드프레스 연결에 실패했습니다. 게시 시뮬레이션을 실행합니다.")
                publisher.simulate_publish(title, content)
        else:
            print("블로그 제목 또는 내용을 추출할 수 없습니다.")
    else:
        print("처리할 블로그 내용이 없습니다.")

if __name__ == "__main__":
    main() 