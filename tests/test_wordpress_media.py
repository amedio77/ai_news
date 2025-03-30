import os
from src.integrations.wordpress.media_manager import WordPressMediaManager

def test_image_upload():
    """WordPress 이미지 업로드 테스트"""
    media_manager = WordPressMediaManager()
    
    # 테스트 이미지 생성
    test_image_path = "tests/test_image.jpg"
    
    # 테스트 이미지가 없으면 생성
    if not os.path.exists(test_image_path):
        from PIL import Image
        img = Image.new('RGB', (800, 600), color='white')
        img.save(test_image_path)
    
    try:
        print("\n1. 단일 이미지 업로드 테스트")
        result = media_manager.upload_image(
            image_path=test_image_path,
            alt_text="테스트 이미지",
            caption="이것은 테스트 이미지입니다.",
            description="WordPress 이미지 업로드 테스트를 위한 이미지입니다."
        )
        
        if result:
            print("이미지 업로드 성공!")
            print(f"이미지 URL: {result['url']}")
            print(f"이미지 ID: {result['id']}")
            print(f"이미지 제목: {result.get('title', '')}")
            
            # HTML 태그 생성 테스트
            html = media_manager.get_image_html_for_content(result)
            print("\n생성된 HTML:")
            print(html)
        else:
            print("이미지 업로드 실패!")
        
        print("\n2. 배치 이미지 업로드 테스트")
        batch_results = media_manager.upload_images_batch(
            image_paths=[test_image_path, test_image_path],
            alt_texts=["테스트 이미지 1", "테스트 이미지 2"],
            captions=["첫 번째 테스트 이미지", "두 번째 테스트 이미지"]
        )
        
        if batch_results:
            print(f"배치 업로드 성공! {len(batch_results)}개의 이미지가 업로드되었습니다.")
            for idx, img in enumerate(batch_results, 1):
                print(f"\n이미지 {idx}:")
                print(f"URL: {img['url']}")
                print(f"ID: {img['id']}")
        else:
            print("배치 업로드 실패!")
            
    finally:
        # 테스트 이미지 정리
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == '__main__':
    test_image_upload() 