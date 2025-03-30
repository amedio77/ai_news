import unittest
import os
from datetime import datetime
from src.crawlers.rss_crawler import RSSNewsCrawler

class TestRSSCrawler(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
        self.crawler = RSSNewsCrawler()
    
    def test_1_crawl_general_feeds(self):
        """일반 뉴스 피드 크롤링 테스트"""
        print("\n1. 일반 뉴스 피드 크롤링 테스트")
        news_list = self.crawler.crawl_rss_feeds(feed_type='general', max_items_per_feed=5)
        self.assertIsInstance(news_list, list)
        print(f"수집된 뉴스 수: {len(news_list)}")
        if news_list:
            print("\n첫 번째 뉴스:")
            print(f"제목: {news_list[0]['title']}")
            print(f"발행일: {news_list[0]['published']}")
            print(f"출처: {news_list[0]['source']}")
    
    def test_2_crawl_specialized_feeds(self):
        """전문 뉴스 피드 크롤링 테스트"""
        print("\n2. 전문 뉴스 피드 크롤링 테스트")
        news_list = self.crawler.crawl_rss_feeds(feed_type='specialized', max_items_per_feed=5)
        self.assertIsInstance(news_list, list)
        print(f"수집된 뉴스 수: {len(news_list)}")
        if news_list:
            print("\n첫 번째 뉴스:")
            print(f"제목: {news_list[0]['title']}")
            print(f"발행일: {news_list[0]['published']}")
            print(f"출처: {news_list[0]['source']}")
    
    def test_3_save_news_data(self):
        """뉴스 데이터 저장 테스트"""
        print("\n3. 뉴스 데이터 저장 테스트")
        # 테스트용 뉴스 데이터 생성
        test_news = [{
            'title': '[테스트] AI 기술 발전 소식',
            'summary': '이것은 테스트 뉴스 내용입니다.',
            'link': 'https://test.news/article/1',
            'published': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': '테스트 뉴스'
        }]
        
        # 데이터 저장
        file_path = self.crawler.save_news_data(test_news, 'test_news.json')
        self.assertTrue(os.path.exists(file_path))
        print(f"저장된 파일 경로: {file_path}")
    
    def test_4_crawl_and_save(self):
        """크롤링 및 저장 통합 테스트"""
        print("\n4. 크롤링 및 저장 통합 테스트")
        file_path, news_data = self.crawler.crawl_and_save(feed_type='all', max_items_per_feed=5)
        self.assertTrue(os.path.exists(file_path))
        print(f"저장된 파일 경로: {file_path}")
        print(f"수집된 뉴스 수: {len(news_data)}")
        if news_data:
            print("\n첫 번째 뉴스:")
            print(f"제목: {news_data[0]['user_name']}")  # Twitter 형식으로 변환된 데이터
            print(f"내용: {news_data[0]['tweet_text']}")
            print(f"작성일: {news_data[0]['created_at']}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 