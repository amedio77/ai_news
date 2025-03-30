import unittest
from src.integrations.wordpress.publisher import WordPressPublisher

class TestWordPressIntegration(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
        self.publisher = WordPressPublisher()
    
    def test_1_connection(self):
        """WordPress 연결 테스트"""
        print("\n1. WordPress 연결 테스트")
        result = self.publisher.connect_to_wordpress()
        self.assertTrue(result, "WordPress 연결 실패")
    
    def test_2_create_draft_post(self):
        """초안 포스트 생성 테스트"""
        print("\n2. 초안 포스트 생성 테스트")
        result = self.publisher.publish_blog(
            title="[테스트] 초안 포스트",
            content="이것은 테스트 초안 포스트입니다.",
            status="draft",
            tags=["테스트", "자동화"]
        )
        self.assertIsNotNone(result, "초안 포스트 생성 실패")
        print(f"생성된 포스트 URL: {result['url']}")
        print(f"포스트 상태: {result['status']}")
        self.assertEqual(result['status'], 'draft')
        
        # 생성된 포스트 ID 저장
        self.draft_post_id = result['id']
    
    def test_3_create_post_with_categories(self):
        """카테고리가 있는 포스트 생성 테스트"""
        print("\n3. 카테고리 포스트 생성 테스트")
        result = self.publisher.publish_blog(
            title="[테스트] 카테고리 포스트",
            content="이것은 카테고리가 있는 테스트 포스트입니다.",
            status="draft",
            categories=[1],  # 기본 카테고리 (미분류)
            tags=["테스트", "카테고리"]
        )
        self.assertIsNotNone(result, "카테고리 포스트 생성 실패")
        print(f"생성된 포스트 URL: {result['url']}")
        self.assertIn('categories', result)
    
    def test_4_create_post_with_tags(self):
        """태그가 있는 포스트 생성 테스트"""
        print("\n4. 태그 포스트 생성 테스트")
        result = self.publisher.publish_blog(
            title="[테스트] 태그 포스트",
            content="이것은 태그가 있는 테스트 포스트입니다.",
            status="draft",
            tags=["자동화테스트", "통합테스트", "WordPress"]
        )
        self.assertIsNotNone(result, "태그 포스트 생성 실패")
        print(f"생성된 포스트 URL: {result['url']}")
        self.assertIn('tags', result)

def run_tests():
    """테스트 실행"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWordPressIntegration)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run_tests() 