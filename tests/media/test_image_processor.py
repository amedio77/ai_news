import unittest
import os
import tempfile
from PIL import Image
from src.media.image_processor import ImageProcessor

class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        """테스트 실행 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.image_processor = ImageProcessor(images_dir=self.temp_dir)
        
        # 테스트용 이미지 생성
        self.test_image_path = os.path.join(self.temp_dir, "test_image.png")
        test_image = Image.new('RGB', (2000, 2000), color='red')
        test_image.save(self.test_image_path)

    def tearDown(self):
        """테스트 실행 후 정리"""
        # 테스트 파일 삭제
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        
        # 이미지 프로세서의 임시 파일 정리
        self.image_processor.cleanup_temp_files()
        
        # 임시 디렉토리 삭제
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_optimize_image(self):
        """이미지 최적화 테스트"""
        result = self.image_processor.optimize_image(
            self.test_image_path,
            max_size=800,
            quality=85,
            format='JPEG'
        )
        
        self.assertTrue(os.path.exists(result['optimized_path']))
        optimized_image = Image.open(result['optimized_path'])
        self.assertLessEqual(optimized_image.size[0], 800)
        self.assertLessEqual(optimized_image.size[1], 800)

    def test_process_image_for_web(self):
        """웹용 이미지 처리 테스트"""
        result = self.image_processor.process_image_for_web(
            self.test_image_path,
            alt_text="Test image",
            caption="Test caption"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('original_path', result)
        self.assertIn('optimized_path', result)
        self.assertIn('alt_text', result)
        self.assertIn('caption', result)
        self.assertEqual(result['alt_text'], "Test image")
        self.assertEqual(result['caption'], "Test caption")

    def test_get_image_html(self):
        """이미지 HTML 생성 테스트"""
        image_info = {
            'optimized_path': '/path/to/image.jpg',
            'alt_text': 'Test image',
            'caption': 'Test caption'
        }
        
        html = self.image_processor.get_image_html(image_info)
        self.assertIn('<img', html)
        self.assertIn('alt="Test image"', html)
        self.assertIn('Test caption', html)

if __name__ == '__main__':
    unittest.main() 