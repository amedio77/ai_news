from src.integrations.google.sheets_integration import GoogleSheetsManager
from datetime import datetime
import os
from dotenv import load_dotenv

def test_save_to_sheet():
    # 환경 변수 로드
    load_dotenv()
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    
    # 테스트 데이터 생성
    test_data = [
        {
            "title": "[테스트] OpenAI가 GPT-5 발표",
            "content": "OpenAI가 새로운 AI 모델 GPT-5를 발표했습니다. 이전 모델보다 2배 더 강력해졌다고 합니다.",
            "source": "테크뉴스",
            "url": "https://tech.news/gpt5-announcement",
            "date": datetime.now().strftime('%Y-%m-%d')
        },
        {
            "tweet_text": "구글이 새로운 AI 칩을 발표했습니다! 기존 TPU보다 성능이 3배 향상되었다고 하네요 #AI #Google",
            "created_at": datetime.now().strftime('%a %b %d %H:%M:%S +0000 %Y'),
            "source": "Twitter",
            "tweet_url": "https://twitter.com/technews/status/123456789"
        }
    ]

    # 구글 시트 매니저 초기화
    sheets_manager = GoogleSheetsManager()

    # 구글 API 인증
    print("\n1. 구글 API 인증 시도...")
    if not sheets_manager.authenticate():
        print("구글 API 인증 실패")
        return

    # 구글 시트 열기
    print("\n2. 구글 시트 열기 시도...")
    if not sheets_manager.open_spreadsheet():
        print("구글 시트 열기 실패")
        return

    print(f"시트 제목: {sheets_manager.sheet.title}")
    print(f"시트 ID: {sheets_manager.sheet.id}")

    # 데이터 저장
    print("\n3. 테스트 데이터 저장 시도...")
    result = sheets_manager.save_news_to_sheet(test_data, "AI_뉴스_데이터")
    
    if result:
        print("\n테스트 완료! 구글 시트를 확인해주세요.")
        print(f"시트 URL: https://docs.google.com/spreadsheets/d/{sheets_manager.sheet.id}")
    else:
        print("데이터 저장 실패")

if __name__ == "__main__":
    test_save_to_sheet() 