import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from src.integrations.wordpress.publisher import WordPressPublisher

class TestWordPressPublisher(unittest.TestCase):
    def setUp(self):
        """테스트 실행 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.publisher = WordPressPublisher(
            wp_url="https://test.com",
            wp_username="test_user",
            wp_password="test_pass"
        )
        
        # 테스트 마크다운 파일 생성
        self.test_md_path = os.path.join(self.temp_dir, "test_blog.md")
        with open(self.test_md_path, 'w') as f:
            f.write("# Test Title\n\nTest content with ![Test image](test.jpg)")

    def tearDown(self):
        """테스트 실행 후 정리"""
        if os.path.exists(self.test_md_path):
            os.remove(self.test_md_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_load_blog_content(self):
        """블로그 컨텐츠 로드 테스트"""
        content = self.publisher.load_blog_content(self.test_md_path)
        self.assertIsNotNone(content)
        self.assertIn("# Test Title", content)
        self.assertIn("![Test image](test.jpg)", content)

    def test_extract_title_and_content(self):
        """제목과 컨텐츠 추출 테스트"""
        markdown_text = "# Test Title\n\nTest content"
        title, content = self.publisher.extract_title_and_content(markdown_text)
        
        self.assertEqual(title, "Test Title")
        self.assertEqual(content.strip(), "Test content")

    def test_extract_image_descriptions(self):
        """이미지 설명 추출 테스트"""
        content = "Content with ![Alt text 1](image1.jpg) and ![Alt text 2](image2.jpg)"
        descriptions = self.publisher.extract_image_descriptions(content)
        
        self.assertEqual(len(descriptions), 2)
        self.assertEqual(descriptions[0]['alt_text'], "Alt text 1")
        self.assertEqual(descriptions[0]['path'], "image1.jpg")
        self.assertEqual(descriptions[1]['alt_text'], "Alt text 2")
        self.assertEqual(descriptions[1]['path'], "image2.jpg")

    @patch('xmlrpc.client.ServerProxy')
    def test_publish_blog(self, mock_server_proxy):
        """블로그 발행 테스트"""
        mock_server = MagicMock()
        mock_server.wp.newPost.return_value = "123"
        mock_server_proxy.return_value = mock_server
        
        result = self.publisher.publish_blog(
            self.test_md_path,
            categories=["Test"],
            tags=["test"],
            status="draft"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result, "https://test.com/?p=123")
        mock_server.wp.newPost.assert_called_once()

    def test_convert_markdown_to_html(self):
        """마크다운을 HTML로 변환 테스트"""
        markdown_text = "# Test Title\n\nTest **bold** content"
        html = self.publisher.convert_markdown_to_html(markdown_text)
        
        self.assertIn("<h1>Test Title</h1>", html)
        self.assertIn("<strong>bold</strong>", html)

if __name__ == '__main__':
    unittest.main() 