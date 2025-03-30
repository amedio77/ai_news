#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
이미지 처리 및 최적화 모듈
"""

import os
import json
from typing import Optional, Tuple, Dict
from PIL import Image
import datetime

from ..core.config import Config
from ..core.utils import save_metadata

class ImageProcessor:
    """이미지 처리 및 최적화 클래스"""
    
    def __init__(self, images_dir: str = None):
        """초기화 함수
        
        Args:
            images_dir (str, optional): 이미지 저장 디렉토리
        """
        self.images_dir = images_dir or Config.IMAGES_DIR
        
        # 디렉토리 생성
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
    
    def optimize_image(self, image_path: str, max_size: int = 1024,
                      quality: int = 85, format: str = 'PNG') -> Dict:
        """이미지 최적화
        
        Args:
            image_path (str): 원본 이미지 경로
            max_size (int): 최대 크기 (가로/세로)
            quality (int): 이미지 품질 (1-100)
            format (str): 저장할 이미지 포맷
            
        Returns:
            Dict: 최적화된 이미지 정보
        """
        try:
            # 이미지 열기
            with Image.open(image_path) as img:
                # 이미지 크기 조정
                if img.size[0] > max_size or img.size[1] > max_size:
                    img.thumbnail((max_size, max_size))
                
                # 파일명 생성
                filename = os.path.basename(image_path)
                name, _ = os.path.splitext(filename)
                optimized_filename = f"{name}_optimized.{format.lower()}"
                optimized_path = os.path.join(self.images_dir, optimized_filename)
                
                # 이미지 저장
                img.save(optimized_path, format=format, quality=quality)
                print(f"최적화된 이미지가 {optimized_path}에 저장되었습니다.")
                
                return {
                    'original_path': image_path,
                    'optimized_path': optimized_path,
                    'width': img.size[0],
                    'height': img.size[1],
                    'format': format,
                    'quality': quality
                }
        except Exception as e:
            print(f"이미지 최적화 중 오류 발생: {str(e)}")
            return None
    
    def process_image_for_web(self, image_path: str, alt_text: str = '',
                            caption: str = '') -> Dict:
        """웹용 이미지 처리
        
        Args:
            image_path (str): 이미지 파일 경로
            alt_text (str): 대체 텍스트
            caption (str): 이미지 설명
            
        Returns:
            Dict: 처리된 이미지 정보
        """
        try:
            # 이미지 최적화
            optimized = self.optimize_image(image_path)
            if not optimized:
                return None
            
            # 이미지 정보 구성
            return {
                'original_path': image_path,
                'optimized_path': optimized['optimized_path'],
                'path': optimized['optimized_path'],
                'url': os.path.basename(optimized['optimized_path']),
                'alt_text': alt_text,
                'caption': caption,
                'width': optimized['width'],
                'height': optimized['height'],
                'mime_type': f"image/{optimized['format'].lower()}"
            }
        except Exception as e:
            print(f"이미지 처리 중 오류 발생: {str(e)}")
            return None
    
    def process_images_batch(self, image_paths: list, alt_texts: list = None,
                           captions: list = None) -> list:
        """이미지 일괄 처리
        
        Args:
            image_paths (list): 이미지 파일 경로 리스트
            alt_texts (list, optional): 대체 텍스트 리스트
            captions (list, optional): 캡션 리스트
            
        Returns:
            list: 처리된 이미지 정보 리스트
        """
        processed_images = []
        
        for i, image_path in enumerate(image_paths):
            alt_text = alt_texts[i] if alt_texts and i < len(alt_texts) else ""
            caption = captions[i] if captions and i < len(captions) else ""
            
            image_info = self.process_image_for_web(image_path, alt_text, caption)
            if image_info:
                processed_images.append(image_info)
        
        return processed_images
    
    def get_image_html(self, image_info: Dict) -> str:
        """이미지 HTML 태그 생성
        
        Args:
            image_info (Dict): 이미지 정보 딕셔너리
            
        Returns:
            str: 이미지 HTML 태그
        """
        # 기본 이미지 태그
        html = f'<img src="{image_info.get("path") or image_info.get("url")}" '
        html += f'alt="{image_info.get("alt_text", "")}" '
        
        # 크기 정보가 있으면 추가
        if "width" in image_info and "height" in image_info:
            html += f'width="{image_info["width"]}" '
            html += f'height="{image_info["height"]}" '
        
        html += '/>'

        # 캡션이 있으면 figure 태그로 감싸기
        if image_info.get("caption"):
            html = f'<figure>{html}<figcaption>{image_info["caption"]}</figcaption></figure>'

        return html 

    def cleanup_temp_files(self):
        """임시 파일 정리"""
        try:
            if os.path.exists(self.images_dir):
                for filename in os.listdir(self.images_dir):
                    file_path = os.path.join(self.images_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        print(f"파일 삭제 중 오류 발생: {str(e)}")
                os.rmdir(self.images_dir)
        except Exception as e:
            print(f"임시 파일 정리 중 오류 발생: {str(e)}") 