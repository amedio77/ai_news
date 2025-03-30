import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from src.integrations.wordpress.media_manager import WordPressMediaManager

class TestWordPressMediaManager(unittest.TestCase):
    def setUp(self):
        """테스트 실행 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.media_manager = WordPressMediaManager(
            wp_url="https://test.com",
            wp_username="test_user",
            wp_password="test_pass"
        )
        
        # 테스트 파일 생성
        self.test_file_path = os.path.join(self.temp_dir, "test_file.txt")
        with open(self.test_file_path, 'w') as f:
            f.write("Test content")

    def tearDown(self):
        """테스트 실행 후 정리"""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    @patch('xmlrpc.client.ServerProxy')
    def test_connect_to_wordpress(self, mock_server_proxy):
        """WordPress 연결 테스트"""
        mock_server = MagicMock()
        mock_server_proxy.return_value = mock_server
        
        result = self.media_manager.connect_to_wordpress()
        self.assertTrue(result)
        mock_server_proxy.assert_called_once_with("https://test.com/xmlrpc.php")

    @patch('xmlrpc.client.ServerProxy')
    def test_upload_media(self, mock_server_proxy):
        """미디어 업로드 테스트"""
        mock_server = MagicMock()
        mock_server.wp.uploadFile.return_value = {
            'id': '123',
            'url': 'https://test.com/media/test.jpg'
        }
        mock_server_proxy.return_value = mock_server
        
        self.media_manager.connect_to_wordpress()
        result = self.media_manager.upload_media(
            self.test_file_path,
            title="Test File",
            caption="Test Caption"
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], '123')
        self.assertEqual(result['url'], 'https://test.com/media/test.jpg')

    def test_get_image_html_for_content(self):
        """컨텐츠용 이미지 HTML 생성 테스트"""
        image_info = {
            'url': 'https://test.com/media/test.jpg',
            'alt_text': 'Test image',
            'caption': 'Test caption'
        }
        
        html = self.media_manager.get_image_html_for_content(
            image_info,
            size='large',
            alignment='center'
        )
        
        self.assertIn('<img', html)
        self.assertIn('src="https://test.com/media/test.jpg"', html)
        self.assertIn('alt="Test image"', html)
        self.assertIn('Test caption', html)
        self.assertIn('align="center"', html)

if __name__ == '__main__':
    unittest.main() 