import unittest
import json
import os
from src.processors.gpt_processor import GPTProcessor

class TestBlogContent(unittest.TestCase):
    def setUp(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.gpt_processor = GPTProcessor(api_key=api_key)
        self.test_news_file = 'data/crawled/ai_news_rss_20250330.json'
        
    def test_prompt_structure(self):
        """프롬프트 구조 검증"""
        with open('config/prompts.json', 'r', encoding='utf-8') as f:
            prompts = json.load(f)
            
        # 필수 프롬프트 키 확인
        self.assertIn('content_generation', prompts)
        self.assertIn('news_analysis', prompts)
        
        # 콘텐츠 생성 프롬프트 구조 확인
        content_gen = prompts['content_generation']
        self.assertIn('news_blog_post_intro', content_gen)
        self.assertIn('news_blog_post_trends', content_gen)
        self.assertIn('news_blog_post_conclusion', content_gen)
        self.assertIn('meta_description', content_gen)
        
        # 각 프롬프트의 필수 필드 확인
        for key in ['news_blog_post_intro', 'news_blog_post_trends', 'news_blog_post_conclusion']:
            self.assertIn('role', content_gen[key])
            self.assertIn('content', content_gen[key])
            
    def test_generate_blog_post(self):
        """크롤링된 뉴스로 블로그 포스트 생성 테스트"""
        post_content, meta = self.gpt_processor.generate_blog_post(self.test_news_file)
        
        # 생성된 콘텐츠 출력
        print("\n=== 생성된 블로그 포스트 ===\n")
        print(post_content)
        print("\n=== 메타 설명 ===\n")
        print(meta)
        print("\n=== 콘텐츠 길이 ===\n")
        print(f"본문 길이: {len(post_content)}자")
        print(f"메타 설명 길이: {len(meta)}자")
        
        # 검증
        self.assertGreater(len(post_content), 2000)  # 최소 2000자
        self.assertGreater(len(meta), 120)      # 최소 120자
        self.assertLess(len(meta), 160)         # 최대 160자

if __name__ == '__main__':
    unittest.main() 