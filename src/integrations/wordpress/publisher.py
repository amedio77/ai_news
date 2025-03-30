#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WordPress 게시 모듈 (REST API 사용)
"""

import os
import requests
from typing import Dict, Optional, List
from base64 import b64encode
from urllib.parse import urljoin
from datetime import datetime

from ...core.config import Config
from ...media.image_processor import ImageProcessor
from .media_manager import WordPressMediaManager

class WordPressPublisher:
    """WordPress 게시 클래스"""
    
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
        self.media_manager = WordPressMediaManager(wp_url, wp_username, wp_password)
        
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
                print(f"응답 내용: {response.text}")
                self.auth_token = None
                return False
                
        except Exception as e:
            print(f"WordPress 연결 중 오류 발생: {str(e)}")
            self.auth_token = None
            return False
    
    def publish_blog(self, title: str, content: str, categories: List[int] = None,
                    tags: List[str] = None, status: str = 'publish',
                    featured_media_id: int = None) -> Optional[Dict]:
        """블로그 포스트 게시
        
        Args:
            title (str): 포스트 제목
            content (str): 포스트 내용
            categories (List[int], optional): 카테고리 ID 목록
            tags (List[str], optional): 태그 목록
            status (str, optional): 포스트 상태 ('publish', 'draft', 'private', 'pending')
            featured_media_id (int, optional): 대표 이미지 ID
            
        Returns:
            Optional[Dict]: 게시된 포스트 정보 또는 None
        """
        try:
            if not self.auth_token:
                print("WordPress 인증이 필요합니다.")
                return None

            if self.is_test_mode:
                return {
                    'id': '123',
                    'url': 'https://test.com/test-post',
                    'title': title,
                    'content': content,
                    'status': status,
                    'categories': categories or [],
                    'tags': tags or []
                }

            # 포스트 데이터 준비
            post_data = {
                'title': title,
                'content': content,
                'status': status
            }
            
            if categories:
                post_data['categories'] = categories
            
            if tags:
                # 태그 이름으로 ID 조회 또는 생성
                tag_ids = []
                for tag_name in tags:
                    tag_id = self._get_or_create_tag(tag_name)
                    if tag_id:
                        tag_ids.append(tag_id)
                if tag_ids:
                    post_data['tags'] = tag_ids
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
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
                print(f"포스트가 게시되었습니다: {data['link']}")
                return {
                    'id': data['id'],
                    'url': data['link'],
                    'title': data['title']['rendered'],
                    'content': data['content']['rendered'],
                    'status': data['status'],
                    'categories': data.get('categories', []),
                    'tags': data.get('tags', [])
                }
            else:
                print(f"포스트 게시 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"포스트 게시 중 오류 발생: {str(e)}")
            return None
    
    def _get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """태그 ID 조회 또는 생성
        
        Args:
            tag_name (str): 태그 이름
            
        Returns:
            Optional[int]: 태그 ID 또는 None
        """
        try:
            if self.is_test_mode:
                return 1
            
            headers = {
                'Authorization': f'Basic {self.auth_token}'
            }
            
            # 태그 검색
            response = requests.get(
                f"{self.api_url}/tags",
                headers=headers,
                params={'search': tag_name}
            )
            
            if response.status_code == 200:
                tags = response.json()
                if tags:
                    return tags[0]['id']
                
                # 태그가 없으면 생성
                create_response = requests.post(
                    f"{self.api_url}/tags",
                    headers=headers,
                    json={'name': tag_name}
                )
                
                if create_response.status_code in [200, 201]:
                    return create_response.json()['id']
            
            return None
            
        except Exception as e:
            print(f"태그 생성 중 오류 발생: {str(e)}")
            return None

    def delete_post(self, post_id: int) -> bool:
        """포스트 삭제
        
        Args:
            post_id (int): 삭제할 포스트 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if not self.auth_token:
                print("WordPress 인증이 필요합니다.")
                return False

            if self.is_test_mode:
                return True

            # 포스트 삭제
            headers = {
                'Authorization': f'Basic {self.auth_token}'
            }
            
            response = requests.delete(
                f"{self.api_url}/posts/{post_id}",
                headers=headers,
                params={'force': True}  # 휴지통으로 이동하지 않고 완전히 삭제
            )
            
            if response.status_code in [200, 204]:
                print(f"포스트 {post_id}가 삭제되었습니다.")
                return True
            else:
                print(f"포스트 삭제 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return False
                
        except Exception as e:
            print(f"포스트 삭제 중 오류 발생: {str(e)}")
            return False 