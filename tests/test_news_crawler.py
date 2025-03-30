import unittest
import os
from src.crawlers.news_crawler import NewsCrawler

class TestNewsCrawler(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
        self.crawler = NewsCrawler()
        self.test_output_dir = "output/test_crawling"
        
        # 출력 디렉토리 생성
        os.makedirs(self.test_output_dir, exist_ok=True)
    
    def test_1_zdnet_crawling(self):
        """ZDNet Korea 크롤링 테스트"""
        print("\n1. ZDNet Korea 크롤링 테스트")
        news_list = self.crawler.crawl_news('zdnet')
        
        self.assertIsInstance(news_list, list)
        self.assertGreater(len(news_list), 0)
        
        # 첫 번째 뉴스 데이터 구조 확인
        first_news = news_list[0]
        self.assertIn('title', first_news)
        self.assertIn('content', first_news)
        self.assertIn('url', first_news)
        self.assertIn('source', first_news)
        self.assertIn('created_at', first_news)
        
        print(f"크롤링된 뉴스 개수: {len(news_list)}")
        print("\n첫 번째 뉴스:")
        print(f"제목: {first_news['title']}")
        print(f"내용: {first_news['content'][:100]}...")
        print(f"URL: {first_news['url']}")
    
    def test_2_aitimes_crawling(self):
        """AI Times 크롤링 테스트"""
        print("\n2. AI Times 크롤링 테스트")
        news_list = self.crawler.crawl_news('aitimes')
        
        self.assertIsInstance(news_list, list)
        self.assertGreater(len(news_list), 0)
        
        # 첫 번째 뉴스 데이터 구조 확인
        first_news = news_list[0]
        self.assertIn('title', first_news)
        self.assertIn('content', first_news)
        self.assertIn('url', first_news)
        self.assertIn('source', first_news)
        self.assertIn('created_at', first_news)
        
        print(f"크롤링된 뉴스 개수: {len(news_list)}")
        print("\n첫 번째 뉴스:")
        print(f"제목: {first_news['title']}")
        print(f"내용: {first_news['content'][:100]}...")
        print(f"URL: {first_news['url']}")
    
    def test_3_all_news_crawling(self):
        """전체 뉴스 크롤링 테스트"""
        print("\n3. 전체 뉴스 크롤링 테스트")
        news_list = self.crawler.crawl_all_news()
        
        self.assertIsInstance(news_list, list)
        self.assertGreater(len(news_list), 0)
        
        print(f"총 크롤링된 뉴스 개수: {len(news_list)}")
        
        # 각 사이트별 뉴스 개수 확인
        sources = {}
        for news in news_list:
            source = news['source']
            sources[source] = sources.get(source, 0) + 1
        
        print("\n사이트별 뉴스 개수:")
        for source, count in sources.items():
            print(f"{source}: {count}개")
    
    def test_4_save_to_file(self):
        """뉴스 데이터 저장 테스트"""
        print("\n4. 뉴스 데이터 저장 테스트")
        
        # 뉴스 크롤링
        news_list = self.crawler.crawl_all_news()
        
        # 파일로 저장
        test_file = os.path.join(self.test_output_dir, "test_news.json")
        result = self.crawler.save_to_file(news_list, test_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
        
        print(f"뉴스 데이터가 {test_file}에 저장되었습니다.")

if __name__ == '__main__':
    unittest.main(verbosity=2) 