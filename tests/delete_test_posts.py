from src.integrations.wordpress.publisher import WordPressPublisher

def delete_test_posts():
    """테스트 포스트 삭제"""
    publisher = WordPressPublisher()
    
    # 테스트 포스트 ID 목록
    test_post_ids = [2688, 2689, 2690]
    
    # 각 포스트 삭제
    for post_id in test_post_ids:
        print(f"\n포스트 {post_id} 삭제 시도...")
        if publisher.delete_post(post_id):
            print(f"포스트 {post_id} 삭제 성공")
        else:
            print(f"포스트 {post_id} 삭제 실패")

if __name__ == '__main__':
    delete_test_posts() 