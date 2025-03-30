import openai
import os
import json
import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

class DailyNewsSummaryGenerator:
    def __init__(self, api_key, images_dir):
        self.api_key = api_key
        self.images_dir = images_dir
        
        # 환경 변수 로드
        load_dotenv()
        
        # 이미지 설정 로드
        self.image_size = os.getenv('DEFAULT_IMAGE_SIZE', '1200x670')
        self.image_quality = os.getenv('DEFAULT_IMAGE_QUALITY', 'standard')
        self.image_style = os.getenv('DEFAULT_IMAGE_STYLE', 'tech')

    def generate_image(self, prompt, filename):
        """DALL-E를 사용하여 이미지 생성
        
        Args:
            prompt (str): 이미지 생성 프롬프트
            filename (str): 저장할 파일명
            
        Returns:
            str: 생성된 이미지 파일 경로
        """
        try:
            client = openai.OpenAI(api_key=self.api_key)
            
            # 프롬프트 최적화
            optimized_prompt = f"""
            Create a high-quality, professional image for a daily AI news summary:
            {prompt}
            Style: Modern, journalistic, tech-focused
            Colors: Use a balanced color scheme with professional tones
            Composition: Clean, informative, with clear visual hierarchy
            Text: No text overlay required
            """
            
            # 이미지 생성
            response = client.images.generate(
                model="dall-e-3",
                prompt=optimized_prompt,
                size=self.image_size,
                quality=self.image_quality,
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
                    'size': self.image_size,
                    'quality': self.image_quality,
                    'generation_date': datetime.datetime.now().isoformat()
                }
                
                metadata_path = os.path.join(self.images_dir, f"{os.path.splitext(filename)[0]}_metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                print(f"이미지가 {image_path}에 저장되었습니다.")
                print(f"메타데이터가 {metadata_path}에 저장되었습니다.")
                return image_path
            else:
                print(f"이미지 다운로드 실패: HTTP {response.status_code}")
                return None
            
        except Exception as e:
            print(f"이미지 생성 중 오류 발생: {e}")
            return None
    
    def generate_images_for_summary(self, blog_content):
        """일일 뉴스 요약에 맞는 이미지 생성
        
        Args:
            blog_content (str): 블로그 내용
            
        Returns:
            list: 생성된 이미지 파일 경로 리스트
        """
        try:
            # 이미지 설명 추출
            descriptions = self.extract_image_descriptions(blog_content)
            image_paths = []
            
            # 각 설명에 대해 이미지 생성
            for i, description in enumerate(descriptions, 1):
                # 파일명 생성
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"daily_news_image_{i}_{timestamp}.png"
                
                # 이미지 생성
                image_path = self.generate_image(description, filename)
                if image_path:
                    image_paths.append(image_path)
                else:
                    # 이미지 생성 실패 시 샘플 이미지 사용
                    sample_path = self.generate_sample_image(i)
                    if sample_path:
                        image_paths.append(sample_path)
            
            return image_paths
            
        except Exception as e:
            print(f"일일 뉴스 요약용 이미지 생성 중 오류 발생: {e}")
            return self.generate_sample_images()
    
    def generate_sample_image(self, index):
        """단일 샘플 이미지 생성
        
        Args:
            index (int): 이미지 인덱스
            
        Returns:
            str: 생성된 샘플 이미지 파일 경로
        """
        try:
            # 이미지 크기 및 색상 설정
            width, height = map(int, self.image_size.split('x'))
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
            text = f"AI 일일 뉴스 요약 샘플 이미지 {index}"
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
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"daily_news_sample_{index}_{timestamp}.png"
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
            
            metadata_path = os.path.join(self.images_dir, f"{os.path.splitext(filename)[0]}_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"샘플 이미지가 {image_path}에 저장되었습니다.")
            return image_path
            
        except Exception as e:
            print(f"샘플 이미지 생성 중 오류 발생: {e}")
            return None
    
    def generate_sample_images(self):
        """샘플 이미지 세트 생성
        
        Returns:
            list: 샘플 이미지 파일 경로 리스트
        """
        sample_images = []
        for i in range(1, 4):
            image_path = self.generate_sample_image(i)
            if image_path:
                sample_images.append(image_path)
        return sample_images 