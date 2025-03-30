#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
이미지 생성 모듈
"""

import os
import json
import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
import openai
from typing import List, Optional

from ..core.config import Config
from ..core.utils import save_metadata, format_filename

class ImageGenerator:
    """이미지 생성 클래스"""
    
    def __init__(self, api_key: str = None, images_dir: str = None):
        """초기화 함수
        
        Args:
            api_key (str, optional): OpenAI API 키
            images_dir (str, optional): 이미지 저장 디렉토리
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.images_dir = images_dir or Config.IMAGES_DIR
        
        # 디렉토리 생성
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
    
    def generate_image(self, prompt: str, filename: str, style: str = "tech") -> Optional[str]:
        """DALL-E를 사용하여 이미지 생성
        
        Args:
            prompt (str): 이미지 생성 프롬프트
            filename (str): 저장할 파일명
            style (str): 이미지 스타일 ("tech" 또는 "news")
            
        Returns:
            Optional[str]: 생성된 이미지 파일 경로 또는 None
        """
        try:
            client = openai.OpenAI(api_key=self.api_key)
            
            # 스타일에 따른 프롬프트 최적화
            style_configs = {
                "tech": {
                    "style": "Modern, professional, tech-focused",
                    "colors": "Use a balanced color scheme with blue tones",
                    "composition": "Clean, uncluttered, with clear focal points"
                },
                "news": {
                    "style": "Modern, journalistic, tech-focused",
                    "colors": "Use a balanced color scheme with professional tones",
                    "composition": "Clean, informative, with clear visual hierarchy"
                }
            }
            
            style_config = style_configs.get(style, style_configs["tech"])
            
            # 프롬프트 최적화
            optimized_prompt = f"""
            Create a high-quality, professional image for AI technology content:
            {prompt}
            Style: {style_config['style']}
            Colors: {style_config['colors']}
            Composition: {style_config['composition']}
            Text: No text overlay required
            """
            
            # 이미지 생성
            response = client.images.generate(
                model="dall-e-3",
                prompt=optimized_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # 이미지 다운로드 및 저장
            image_path = os.path.join(self.images_dir, filename)
            response = requests.get(image_url)
            
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                # 이미지 메타데이터 저장
                metadata = {
                    'prompt': prompt,
                    'optimized_prompt': optimized_prompt,
                    'model': 'dall-e-3',
                    'size': '1024x1024',
                    'quality': 'standard',
                    'style': style,
                    'generation_date': datetime.datetime.now().isoformat()
                }
                
                save_metadata(image_path, metadata, Config.METADATA_DIR)
                
                print(f"이미지가 {image_path}에 저장되었습니다.")
                return image_path
            else:
                print(f"이미지 다운로드 실패: HTTP {response.status_code}")
                return None
            
        except Exception as e:
            print(f"이미지 생성 중 오류 발생: {e}")
            return None
    
    def generate_images_for_content(self, content: str, descriptions: List[str], 
                                  base_filename: str = "ai_image", style: str = "tech") -> List[str]:
        """콘텐츠용 이미지 생성
        
        Args:
            content (str): 블로그 내용
            descriptions (List[str]): 이미지 설명 리스트
            base_filename (str): 기본 파일명
            style (str): 이미지 스타일
            
        Returns:
            List[str]: 생성된 이미지 파일 경로 리스트
        """
        try:
            image_paths = []
            
            # 각 설명에 대해 이미지 생성
            for i, description in enumerate(descriptions, 1):
                # 파일명 생성
                filename = format_filename(base_filename, i) + ".png"
                
                # 이미지 생성
                image_path = self.generate_image(description, filename, style)
                if image_path:
                    image_paths.append(image_path)
                else:
                    # 이미지 생성 실패 시 샘플 이미지 사용
                    sample_path = self.generate_sample_image(i, base_filename)
                    if sample_path:
                        image_paths.append(sample_path)
            
            return image_paths
            
        except Exception as e:
            print(f"콘텐츠용 이미지 생성 중 오류 발생: {e}")
            return self.generate_sample_images(base_filename)
    
    def generate_sample_image(self, index: int, base_filename: str = "sample") -> Optional[str]:
        """단일 샘플 이미지 생성
        
        Args:
            index (int): 이미지 인덱스
            base_filename (str): 기본 파일명
            
        Returns:
            Optional[str]: 생성된 샘플 이미지 파일 경로 또는 None
        """
        try:
            # 이미지 크기 및 색상 설정
            width, height = 1024, 1024
            background_color = (73, 109, 137)
            text_color = (255, 255, 255)
            
            # 이미지 생성
            img = Image.new('RGB', (width, height), color=background_color)
            d = ImageDraw.Draw(img)
            
            # 텍스트 설정
            try:
                font_size = 48
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = None
            
            # 텍스트 추가
            text = f"AI 콘텐츠 샘플 이미지 {index}"
            if font:
                # 텍스트 위치 계산 (중앙 정렬)
                text_bbox = d.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = (width - text_width) // 2
                text_y = (height - text_height) // 2
                d.text((text_x, text_y), text, fill=text_color, font=font)
            else:
                # 폰트를 찾을 수 없는 경우 기본 폰트 사용
                d.text((width//4, height//2), text, fill=text_color)
            
            # 이미지 저장
            filename = format_filename(f"{base_filename}_sample", index) + ".png"
            image_path = os.path.join(self.images_dir, filename)
            img.save(image_path, 'PNG', quality=95)
            
            # 메타데이터 저장
            metadata = {
                'type': 'sample_image',
                'index': index,
                'size': (width, height),
                'background_color': background_color,
                'text_color': text_color,
                'generation_date': datetime.datetime.now().isoformat()
            }
            
            save_metadata(image_path, metadata, Config.METADATA_DIR)
            
            print(f"샘플 이미지가 {image_path}에 저장되었습니다.")
            return image_path
            
        except Exception as e:
            print(f"샘플 이미지 생성 중 오류 발생: {e}")
            return None
    
    def generate_sample_images(self, base_filename: str = "sample", count: int = 3) -> List[str]:
        """샘플 이미지 세트 생성
        
        Args:
            base_filename (str): 기본 파일명
            count (int): 생성할 이미지 수
            
        Returns:
            List[str]: 샘플 이미지 파일 경로 리스트
        """
        sample_images = []
        for i in range(1, count + 1):
            image_path = self.generate_sample_image(i, base_filename)
            if image_path:
                sample_images.append(image_path)
        return sample_images 