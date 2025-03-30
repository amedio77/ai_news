#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WordPress 미디어 관리 모듈 (REST API 사용)
"""

import os
import mimetypes
import requests
from typing import Dict, Optional, List
from base64 import b64encode
from urllib.parse import urljoin

from ...core.config import Config
from ...media.image_processor import ImageProcessor

class WordPressMediaManager:
    """WordPress 미디어 관리 클래스"""
    
    def __init__(self, wp_url: str = None, wp_username: str = None, wp_password: str = None):
        """초기화 함수
        
        Args:
            wp_url (str, optional): WordPress URL
            wp_username (str, optional): WordPress 사용자명
            wp_password (str, optional): WordPress 앱 비밀번호
        """
        self.wp_url = wp_url or Config.WP_URL
        self.wp_username = wp_username or Config.WP_USERNAME
        self.wp_password = wp_password or Config.WP_APP_PASSWORD
        self.api_url = urljoin(self.wp_url, 'wp-json/wp/v2')
        self.auth_token = None
        self.image_processor = ImageProcessor()
        
        # 테스트 모드 설정
        self.is_test_mode = self.wp_url.startswith('test.') or self.wp_url == 'test'
        
        self.connect_to_wordpress()
    
    def connect_to_wordpress(self) -> bool:
        """WordPress에 연결 및 인증
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            if self.is_test_mode:
                self.auth_token = "test_token"
                return True
            
            # Basic Auth 토큰 생성
            credentials = f"{self.wp_username}:{self.wp_password}"
            self.auth_token = b64encode(credentials.encode()).decode()
            
            # 연결 테스트
            headers = {
                'Authorization': f'Basic {self.auth_token}'
            }
            response = requests.get(f"{self.api_url}/users/me", headers=headers)
            
            if response.status_code == 200:
                print("WordPress에 연결되었습니다.")
                return True
            else:
                print(f"WordPress 연결 실패: {response.status_code}")
                self.auth_token = None
                return False
                
        except Exception as e:
            print(f"WordPress 연결 중 오류 발생: {str(e)}")
            self.auth_token = None
            return False
    
    def upload_media(self, file_path: str, title: str = None,
                    caption: str = None, description: str = None) -> Optional[Dict]:
        """미디어 파일 업로드

        Args:
            file_path (str): 업로드할 파일 경로
            title (str): 미디어 제목
            caption (str): 미디어 캡션
            description (str): 미디어 설명

        Returns:
            Optional[Dict]: 업로드된 미디어 정보 또는 None
        """
        try:
            if not self.auth_token:
                print("WordPress 인증이 필요합니다.")
                return None

            if self.is_test_mode:
                return {
                    'id': '123',
                    'url': 'https://test.com/test-image.jpg',
                    'title': title,
                    'caption': caption,
                    'description': description,
                    'width': 800,
                    'height': 600
                }

            # 파일 데이터 준비
            with open(file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0])
                }
                
                headers = {
                    'Authorization': f'Basic {self.auth_token}'
                }
                
                # 파일 업로드
                response = requests.post(
                    f"{self.api_url}/media",
                    headers=headers,
                    files=files
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    print(f"미디어 파일이 업로드되었습니다: {data['source_url']}")
                    
                    # 미디어 정보 업데이트
                    if title or caption or description:
                        update_data = {}
                        if title:
                            update_data['title'] = {'rendered': title}
                        if caption:
                            update_data['caption'] = {'rendered': caption}
                        if description:
                            update_data['description'] = {'rendered': description}
                            
                        update_response = requests.post(
                            f"{self.api_url}/media/{data['id']}",
                            headers=headers,
                            json=update_data
                        )
                        
                        if update_response.status_code == 200:
                            data = update_response.json()
                    
                    return {
                        'id': data['id'],
                        'url': data['source_url'],
                        'title': data['title']['rendered'],
                        'caption': data['caption']['rendered'],
                        'description': data['description']['rendered'],
                        'width': data.get('media_details', {}).get('width'),
                        'height': data.get('media_details', {}).get('height')
                    }
                else:
                    print(f"미디어 업로드 실패: {response.status_code}")
                    return None

        except Exception as e:
            print(f"미디어 업로드 중 오류 발생: {str(e)}")
            return None
    
    def upload_image(self, image_path: str, alt_text: str = "",
                    caption: str = "", description: str = "") -> Optional[Dict]:
        """이미지 파일 업로드
        
        Args:
            image_path (str): 이미지 파일 경로
            alt_text (str): 대체 텍스트
            caption (str): 이미지 캡션
            description (str): 이미지 설명
            
        Returns:
            Optional[Dict]: 업로드된 이미지 정보 또는 None
        """
        try:
            # 이미지 처리
            image_info = self.image_processor.process_image_for_web(
                image_path, alt_text, caption
            )
            
            if not image_info:
                return None
            
            # 이미지 업로드
            response = self.upload_media(
                image_info['path'],
                title=alt_text or None,
                caption=caption,
                description=description
            )
            
            if response:
                # 이미지 정보 업데이트
                image_info.update({
                    'id': response['id'],
                    'url': response['url'],
                    'title': response.get('title', ''),
                    'link': response.get('link', '')
                })
                return image_info
            else:
                return None
                
        except Exception as e:
            print(f"이미지 업로드 중 오류 발생: {e}")
            return None
    
    def upload_images_batch(self, image_paths: List[str], alt_texts: List[str] = None,
                          captions: List[str] = None, descriptions: List[str] = None) -> List[Dict]:
        """이미지 일괄 업로드
        
        Args:
            image_paths (List[str]): 이미지 파일 경로 리스트
            alt_texts (List[str], optional): 대체 텍스트 리스트
            captions (List[str], optional): 캡션 리스트
            descriptions (List[str], optional): 설명 리스트
            
        Returns:
            List[Dict]: 업로드된 이미지 정보 리스트
        """
        uploaded_images = []
        
        for i, image_path in enumerate(image_paths):
            alt_text = alt_texts[i] if alt_texts and i < len(alt_texts) else ""
            caption = captions[i] if captions and i < len(captions) else ""
            description = descriptions[i] if descriptions and i < len(descriptions) else ""
            
            image_info = self.upload_image(image_path, alt_text, caption, description)
            if image_info:
                uploaded_images.append(image_info)
        
        return uploaded_images
    
    def get_image_html_for_content(self, image_info: Dict, size: str = 'full',
                                 alignment: str = 'center') -> str:
        """WordPress 콘텐츠용 이미지 HTML 태그 생성
        
        Args:
            image_info (Dict): 이미지 정보 딕셔너리
            size (str): 이미지 크기 ('full', 'large', 'medium', 'thumbnail')
            alignment (str): 정렬 ('left', 'center', 'right')
            
        Returns:
            str: WordPress 이미지 HTML 태그
        """
        # 정렬 속성 설정
        align_attr = f'align="{alignment}"' if alignment in ['left', 'center', 'right'] else ''
        align_class = f"align{alignment}" if alignment in ['left', 'center', 'right'] else ""
        
        # 기본 이미지 태그 생성
        html = f'<img src="{image_info["url"]}" '
        html += f'alt="{image_info.get("alt_text", "")}" '
        
        # 크기 정보가 있으면 추가
        if "width" in image_info and "height" in image_info:
            html += f'width="{image_info["width"]}" '
            html += f'height="{image_info["height"]}" '
        
        html += f'class="size-{size} {align_class}" {align_attr} />'
        
        # 캡션이 있으면 figure 태그로 감싸기
        if image_info.get('caption'):
            html = f'<figure class="wp-caption {align_class}">{html}'
            html += f'<figcaption class="wp-caption-text">{image_info["caption"]}</figcaption>'
            html += '</figure>'
        
        return html 

    def delete_media(self, media_id: int) -> bool:
        """미디어 파일 삭제
        
        Args:
            media_id (int): 삭제할 미디어 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if not self.auth_token:
                print("WordPress 인증이 필요합니다.")
                return False

            if self.is_test_mode:
                return True

            # 미디어 삭제
            headers = {
                'Authorization': f'Basic {self.auth_token}'
            }
            
            response = requests.delete(
                f"{self.api_url}/media/{media_id}",
                headers=headers,
                params={'force': True}  # 휴지통으로 이동하지 않고 완전히 삭제
            )
            
            if response.status_code in [200, 204]:
                print(f"미디어 파일 {media_id}가 삭제되었습니다.")
                return True
            else:
                print(f"미디어 파일 삭제 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return False
                
        except Exception as e:
            print(f"미디어 파일 삭제 중 오류 발생: {str(e)}")
            return False 