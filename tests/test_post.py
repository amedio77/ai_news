from src.integrations.wordpress.publisher import WordPressPublisher

def test_publish_post():
    """WordPress 포스트 게시 테스트"""
    publisher = WordPressPublisher()
    
    # 테스트 포스트 작성
    result = publisher.publish_blog(
        title="테스트 포스트",
        content="이것은 테스트 포스트입니다. API 연결 테스트를 위해 작성되었습니다.",
        status="draft",  # draft로 설정하여 실제로 발행되지 않도록 함
        tags=["테스트"]
    )
    
    if result:
        print("\n포스트 게시 성공!")
        print(f"포스트 URL: {result['url']}")
        print(f"포스트 상태: {result['status']}")
    else:
        print("\n포스트 게시 실패!")

if __name__ == '__main__':
    test_publish_post() 