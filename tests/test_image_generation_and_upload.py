from src.media.image_generator import ImageGenerator
from src.integrations.wordpress.media_manager import WordPressMediaManager
import os

def test_image_generation_and_upload():
    """DALL-E 이미지 생성 및 WordPress 업로드 테스트"""
    
    # 이미지 생성기 및 미디어 매니저 초기화
    image_generator = ImageGenerator()
    media_manager = WordPressMediaManager()
    
    try:
        print("\n1. DALL-E 3로 이미지 생성")
        prompt = "Create a modern, minimalist illustration of artificial intelligence and machine learning, featuring neural networks and data visualization in a clean, professional style."
        image_path = image_generator.generate_image(
            prompt=prompt,
            filename="ai_test_image.png",
            style="tech"
        )
        
        if image_path and os.path.exists(image_path):
            print(f"이미지 생성 성공: {image_path}")
            
            print("\n2. 생성된 이미지를 WordPress에 업로드")
            result = media_manager.upload_image(
                image_path=image_path,
                alt_text="AI and Machine Learning Illustration",
                caption="Modern visualization of artificial intelligence and neural networks",
                description="A minimalist illustration showcasing the concepts of AI and machine learning"
            )
            
            if result:
                print("\n이미지 업로드 성공!")
                print(f"이미지 URL: {result['url']}")
                print(f"이미지 ID: {result['id']}")
                print(f"이미지 제목: {result.get('title', '')}")
                
                # HTML 태그 생성 테스트
                html = media_manager.get_image_html_for_content(result)
                print("\n생성된 HTML:")
                print(html)
                
                return result['id']  # 나중에 삭제하기 위해 ID 반환
            else:
                print("이미지 업로드 실패!")
        else:
            print("이미지 생성 실패!")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")
        return None

def cleanup_test_image(image_id):
    """테스트 이미지 정리"""
    if image_id:
        try:
            # WordPress에서 이미지 삭제
            media_manager = WordPressMediaManager()
            if hasattr(media_manager, 'delete_media'):
                if media_manager.delete_media(image_id):
                    print(f"\n이미지 (ID: {image_id}) 삭제 완료")
                else:
                    print(f"\n이미지 (ID: {image_id}) 삭제 실패")
        except Exception as e:
            print(f"이미지 삭제 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    print("DALL-E 이미지 생성 및 WordPress 업로드 테스트 시작...")
    image_id = test_image_generation_and_upload()
    if image_id:
        cleanup_test_image(image_id) 