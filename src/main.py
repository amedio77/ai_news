#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
메인 실행 스크립트
"""

import os
import argparse
from datetime import datetime
from typing import List, Optional

from core.config import Config
from media.image_generator import ImageGenerator
from integrations.wordpress.publisher import WordPressPublisher
from integrations.wordpress.media_manager import WordPressMediaManager

def load_blog_content(blog_file: str) -> tuple[str, str, List[str], List[str]]:
    """블로그 내용 로드
    
    Args:
        blog_file (str): 블로그 파일 경로
        
    Returns:
        tuple: (제목, 내용, 카테고리, 태그)
    """
    with open(blog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 메타데이터 파싱
    lines = content.split('\n')
    title = ""
    categories = []
    tags = []
    
    in_metadata = False
    metadata_lines = []
    
    for line in lines:
        if line.strip() == '---':
            in_metadata = not in_metadata
            continue
        
        if in_metadata:
            metadata_lines.append(line)
            if line.startswith('title:'):
                title = line.replace('title:', '').strip()
            elif line.startswith('categories:'):
                categories = [cat.strip() for cat in line.replace('categories:', '').strip().split(',')]
            elif line.startswith('tags:'):
                tags = [tag.strip() for tag in line.replace('tags:', '').strip().split(',')]
    
    # 메타데이터 제거
    content_lines = []
    in_metadata = False
    for line in lines:
        if line.strip() == '---':
            in_metadata = not in_metadata
            continue
        if not in_metadata:
            content_lines.append(line)
    
    content = '\n'.join(content_lines).strip()
    
    return title, content, categories, tags

def generate_and_upload_images(content: str, image_descriptions: List[str]) -> List[dict]:
    """이미지 생성 및 업로드
    
    Args:
        content (str): 블로그 내용
        image_descriptions (List[str]): 이미지 설명 리스트
        
    Returns:
        List[dict]: 업로드된 이미지 정보 리스트
    """
    image_generator = ImageGenerator()
    media_manager = WordPressMediaManager()
    uploaded_images = []
    
    # 이미지 생성 및 업로드
    for i, description in enumerate(image_descriptions, 1):
        # 이미지 생성
        filename = f"ai_blog_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.png"
        image_path = image_generator.generate_image(description, filename)
        
        if image_path:
            # 이미지 업로드
            result = media_manager.upload_media(
                image_path,
                title=f"AI Blog Image {i}",
                alt_text=description,
                caption=description
            )
            
            if result:
                uploaded_images.append(result)
                print(f"이미지 {i} 업로드 성공: {result['url']}")
            else:
                print(f"이미지 {i} 업로드 실패")
    
    return uploaded_images

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='블로그 포스트 발행 스크립트')
    parser.add_argument('--publish', action='store_true', help='WordPress에 발행')
    parser.add_argument('--with-images', action='store_true', help='이미지 생성 및 업로드 포함')
    args = parser.parse_args()
    
    try:
        # 최신 블로그 파일 찾기
        blog_dir = os.path.join(Config.OUTPUT_DIR, 'blogs')
        blog_files = [f for f in os.listdir(blog_dir) if f.endswith('.md')]
        if not blog_files:
            print("발행할 블로그 포스트를 찾을 수 없습니다.")
            return
        
        latest_blog = max(blog_files, key=lambda x: os.path.getctime(os.path.join(blog_dir, x)))
        blog_path = os.path.join(blog_dir, latest_blog)
        
        # 블로그 내용 로드
        title, content, categories, tags = load_blog_content(blog_path)
        
        # 이미지 생성 및 업로드
        uploaded_images = []
        if args.with_images:
            image_descriptions = [
                "AI technology and data innovation in financial services, featuring modern visualization of neural networks and data flows",
                "YouTube's AI-driven content management system, showing personalized user experience and notification optimization",
                "AgentSpec framework for enhancing AI agent reliability, illustrated with modern technical diagrams"
            ]
            uploaded_images = generate_and_upload_images(content, image_descriptions)
        
        # 이미지 HTML 추가
        if uploaded_images:
            image_html = "\n\n".join([
                f'<figure class="wp-caption aligncenter">'
                f'<img src="{img["url"]}" alt="{img["alt_text"]}" '
                f'width="{img["width"]}" height="{img["height"]}" '
                f'class="size-full aligncenter" />'
                f'<figcaption class="wp-caption-text">{img["caption"]}</figcaption>'
                f'</figure>'
                for img in uploaded_images
            ])
            content = image_html + "\n\n" + content
        
        # WordPress에 발행
        if args.publish:
            publisher = WordPressPublisher()
            featured_media_id = uploaded_images[0]['id'] if uploaded_images else None
            
            result = publisher.publish_blog(
                title=title,
                content=content,
                categories=categories,
                tags=tags,
                featured_media_id=featured_media_id
            )
            
            if result:
                print(f"블로그 포스트가 발행되었습니다: {result['url']}")
            else:
                print("블로그 포스트 발행 실패")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == '__main__':
    main() 