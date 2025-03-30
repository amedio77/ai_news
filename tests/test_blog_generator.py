#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
블로그 생성기 테스트
"""

import os
import sys
import unittest
from datetime import datetime
from dotenv import load_dotenv

# 상위 디렉토리 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawlers.rss_crawler import RSSNewsCrawler
from src.gpt_integration.blog_generator import GPTBlogGenerator

class TestBlogGenerator(unittest.TestCase):
    """블로그 생성기 테스트 클래스"""
    
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 설정"""
        # 환경 변수 로드
        load_dotenv()
        
        # 디렉토리 설정
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.images_dir = os.path.join(cls.base_dir, 'output', 'images')
        
        # 디렉토리가 없으면 생성
        if not os.path.exists(cls.images_dir):
            os.makedirs(cls.images_dir)
        
        # OpenAI API 키 확인
        cls.api_key = os.getenv('OPENAI_API_KEY')
        if not cls.api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    
    def setUp(self):
        """각 테스트 전 설정"""
        self.crawler = RSSNewsCrawler()
        self.generator = GPTBlogGenerator(self.api_key, self.images_dir)
    
    def test_1_news_collection(self):
        """뉴스 수집 테스트"""
        # 뉴스 수집
        news = self.crawler.crawl_and_save(feed_type='all')
        self.assertIsNotNone(news)
        print(f"\n수집된 뉴스 수: {len(news[1]) if isinstance(news[1], list) else 0}")
    
    def test_2_blog_generation(self):
        """블로그 생성 테스트"""
        # 최신 뉴스 데이터 로드
        data_dir = os.path.join(self.base_dir, 'src', 'data')
        files = [f for f in os.listdir(data_dir) if f.startswith('ai_news_rss_')]
        if not files:
            self.fail("뉴스 데이터 파일을 찾을 수 없습니다.")
        
        latest_file = max(files)
        with open(os.path.join(data_dir, latest_file), 'r', encoding='utf-8') as f:
            import json
            news_data = json.load(f)
        
        # 블로그 생성
        blog_content, blog_path = self.generator.generate_blog(news_data)
        self.assertIsNotNone(blog_content)
        self.assertIsNotNone(blog_path)
        self.assertTrue(os.path.exists(blog_path))
        
        print(f"\n생성된 블로그 미리보기:\n{blog_content[:500]}...")
        print(f"\n전체 블로그는 다음 경로에 저장되었습니다: {blog_path}")
    
    def test_3_image_generation(self):
        """이미지 생성 테스트"""
        # 최신 블로그 파일 찾기
        blogs_dir = os.path.join(self.base_dir, 'output', 'blogs')
        files = [f for f in os.listdir(blogs_dir) if f.startswith('ai_blog_')]
        if not files:
            self.fail("블로그 파일을 찾을 수 없습니다.")
        
        latest_blog = max(files)
        with open(os.path.join(blogs_dir, latest_blog), 'r', encoding='utf-8') as f:
            blog_content = f.read()
        
        # 이미지 생성
        image_paths = self.generator.generate_images_for_blog(blog_content)
        self.assertIsNotNone(image_paths)
        self.assertGreater(len(image_paths), 0)
        
        for path in image_paths:
            self.assertTrue(os.path.exists(path))
            print(f"\n이미지가 생성되었습니다: {path}")

if __name__ == '__main__':
    unittest.main() 