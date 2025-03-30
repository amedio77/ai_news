import openai
import os
import json
import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

class GPTBlogGenerator:
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
            Create a high-quality, professional image for an AI technology blog:
            {prompt}
            Style: Modern, professional, tech-focused
            Colors: Use a balanced color scheme with blue tones
            Composition: Clean, uncluttered, with clear focal points
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
    
    def generate_images_for_blog(self, blog_content):
        """블로그 내용에 맞는 이미지 생성
        
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
                filename = f"ai_blog_image_{i}_{timestamp}.png"
                
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
            print(f"블로그용 이미지 생성 중 오류 발생: {e}")
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
            text = f"AI 뉴스 블로그 샘플 이미지 {index}"
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
            filename = f"sample_image_{index}_{timestamp}.png"
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

    def extract_image_descriptions(self, blog_content):
        """블로그 내용에서 이미지 설명 추출
        
        Args:
            blog_content (str): 블로그 내용
            
        Returns:
            list: 이미지 설명 리스트
        """
        # 섹션별로 이미지 설명 생성
        sections = blog_content.split('\n## ')
        descriptions = []
        
        for section in sections:
            if section.strip():
                # 섹션의 첫 문단을 이미지 설명으로 사용
                paragraphs = section.split('\n\n')
                if paragraphs:
                    # 제목과 첫 문단 조합
                    title = paragraphs[0].strip().replace('#', '').strip()
                    content = paragraphs[1].strip() if len(paragraphs) > 1 else title
                    description = f"{title}: {content}"
                    descriptions.append(description)
        
        return descriptions[:3]  # 최대 3개의 이미지만 생성

    def generate_blog(self, news_data):
        """뉴스 데이터를 기반으로 블로그 글 생성
        
        Args:
            news_data (list): 뉴스 데이터 리스트
            
        Returns:
            tuple: (블로그 내용, 저장된 파일 경로)
        """
        try:
            # GPT 프롬프트 생성
            prompt = """다음 AI 관련 뉴스들을 바탕으로 전문적이고 통찰력 있는 블로그 글을 작성해주세요.

1. 글의 구조:
   - 제목 (흥미롭고 SEO 최적화된)
   - 소개 (핵심 뉴스 요약)
   - 주요 뉴스 분석 (각 뉴스의 의미와 영향)
   - 산업 동향 분석 (뉴스들의 연관성과 트렌드)
   - 시사점 및 전망 (기술/산업/사회적 관점)
   - 결론

2. 작성 스타일:
   - 전문적이고 객관적인 톤
   - 기술적 배경 설명 포함
   - 실제 사례와 데이터 인용
   - 독자의 이해를 돕는 비유와 예시 사용

오늘의 뉴스:
"""
            # 뉴스 데이터 추가
            for news in news_data:
                title = news.get('title', '')
                content = news.get('tweet_text', '') or news.get('description', '')
                source = news.get('source', 'Unknown')
                date = news.get('created_at', '')
                
                prompt += f"\n제목: {title}"
                prompt += f"\n내용: {content}"
                prompt += f"\n출처: {source}"
                prompt += f"\n날짜: {date}\n"
            
            # GPT API 호출
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4",  # 또는 "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "당신은 AI 기술 전문 블로거입니다. 최신 AI 뉴스를 분석하여 통찰력 있는 블로그 글을 작성해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 블로그 내용 추출
            blog_content = response.choices[0].message.content.strip()
            
            # 파일로 저장
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ai_blog_{timestamp}.md"
            filepath = os.path.join(os.path.dirname(self.images_dir), 'blogs', filename)
            
            # 블로그 디렉토리가 없으면 생성
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(blog_content)
            
            print(f"블로그가 {filepath}에 저장되었습니다.")
            return blog_content, filepath
            
        except Exception as e:
            print(f"블로그 생성 중 오류 발생: {e}")
            return None, None 