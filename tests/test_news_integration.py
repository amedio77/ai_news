import unittest
import os
from datetime import datetime
from src.integrations.google.sheets_integration import GoogleSheetsManager

class TestNewsIntegration(unittest.TestCase):
    # 클래스 변수로 시트 ID 저장
    sheet_id = None
    
    def setUp(self):
        """테스트 설정"""
        self.sheets_manager = GoogleSheetsManager()
        
        # 테스트 뉴스 데이터 생성
        self.test_news_data = [
            {
                "title": "[테스트] AI 기술 발전 소식",
                "content": "이것은 테스트 뉴스 내용입니다.",
                "source": "테스트 뉴스",
                "url": "https://test.news/article/1",
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                "tweet_text": "이것은 테스트 트윗입니다. #AI #테스트",
                "created_at": "Wed Mar 29 09:00:00 +0000 2024",
                "source": "Twitter",
                "url": "https://twitter.com/test/status/123456789"
            }
        ]
        
        # 워크시트 제목 설정
        self.worksheet_title = "AI_뉴스_데이터"
    
    def test_1_google_auth(self):
        """구글 API 인증 테스트"""
        print("\n1. 구글 API 인증 테스트")
        result = self.sheets_manager.authenticate()
        self.assertTrue(result, "구글 API 인증 실패")
    
    def test_2_open_spreadsheet(self):
        """구글 시트 열기 테스트"""
        print("\n2. 구글 시트 열기 테스트")
        # 인증 수행
        self.sheets_manager.authenticate()
        result = self.sheets_manager.open_spreadsheet()
        self.assertTrue(result, "구글 시트 열기 실패")
        
        if result:
            # 시트 ID 저장
            TestNewsIntegration.sheet_id = self.sheets_manager.sheet.id
            print(f"시트 제목: {self.sheets_manager.sheet.title}")
            print(f"시트 ID: {self.sheets_manager.sheet.id}")
    
    def test_3_create_worksheet(self):
        """워크시트 생성 테스트"""
        print("\n3. 워크시트 생성 테스트")
        # 인증 및 시트 열기
        self.sheets_manager.authenticate()
        self.sheets_manager.open_spreadsheet(spreadsheet_id=TestNewsIntegration.sheet_id)
        worksheet = self.sheets_manager.get_or_create_worksheet(self.worksheet_title)
        self.assertIsNotNone(worksheet, "워크시트 생성 실패")
        
        if worksheet:
            print(f"워크시트 제목: {worksheet.title}")
            print(f"워크시트 ID: {worksheet.id}")
    
    def test_4_save_news_data(self):
        """뉴스 데이터 저장 테스트"""
        print("\n4. 뉴스 데이터 저장 테스트")
        # 인증 및 시트 열기
        self.sheets_manager.authenticate()
        self.sheets_manager.open_spreadsheet(spreadsheet_id=TestNewsIntegration.sheet_id)
        result = self.sheets_manager.save_news_to_sheet(
            self.test_news_data,
            worksheet_title=self.worksheet_title
        )
        self.assertTrue(result, "뉴스 데이터 저장 실패")
    
    def test_5_verify_saved_data(self):
        """저장된 데이터 확인 테스트"""
        print("\n5. 저장된 데이터 확인 테스트")
        # 인증 및 시트 열기
        self.sheets_manager.authenticate()
        self.sheets_manager.open_spreadsheet(spreadsheet_id=TestNewsIntegration.sheet_id)
        
        # 워크시트 가져오기
        worksheet = self.sheets_manager.get_or_create_worksheet(self.worksheet_title)
        self.assertIsNotNone(worksheet, "워크시트 가져오기 실패")
        
        if worksheet:
            # 모든 데이터 가져오기
            all_values = worksheet.get_all_values()
            
            # 헤더 확인
            self.assertEqual(
                all_values[0],
                ["날짜", "제목", "출처", "내용", "URL", "수집 시간"],
                "헤더가 일치하지 않습니다"
            )
            
            # 최소 데이터 개수 확인 (헤더 + 테스트 데이터)
            self.assertGreaterEqual(
                len(all_values),
                len(self.test_news_data) + 1,
                "저장된 데이터 개수가 최소 기준을 충족하지 않습니다"
            )
            
            print(f"\n전체 데이터 수: {len(all_values)}개")
            print("\n저장된 데이터:")
            for row in all_values:
                print(row)

if __name__ == '__main__':
    unittest.main(verbosity=2) 