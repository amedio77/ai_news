import os
import requests
from base64 import b64encode
from dotenv import load_dotenv

def test_wordpress_connection():
    """WordPress REST API 연결 테스트"""
    # 환경 변수 로드
    load_dotenv()
    
    # WordPress 설정 가져오기
    wp_url = os.getenv('WP_URL')
    wp_username = os.getenv('WP_USERNAME')
    wp_app_password = os.getenv('WP_APP_PASSWORD')
    
    # API URL 설정
    api_url = f"{wp_url}/wp-json/wp/v2"
    
    # Basic Auth 토큰 생성
    credentials = f"{wp_username}:{wp_app_password}"
    auth_token = b64encode(credentials.encode()).decode()
    
    # 헤더 설정
    headers = {
        'Authorization': f'Basic {auth_token}'
    }
    
    try:
        # 사용자 정보 조회 테스트
        response = requests.get(f"{api_url}/users/me", headers=headers)
        
        print(f"\n상태 코드: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print("\n연결 성공!")
            print(f"사용자 이름: {user_data.get('name')}")
            print(f"사용자 역할: {user_data.get('roles')}")
        else:
            print("\n연결 실패!")
            print(f"에러 메시지: {response.text}")
            
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")

if __name__ == '__main__':
    test_wordpress_connection() 