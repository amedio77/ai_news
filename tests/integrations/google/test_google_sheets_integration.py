import unittest
from unittest.mock import MagicMock, patch
import os
import datetime
from src.integrations.google.sheets_integration import GoogleSheetsManager

class TestGoogleSheetsManager(unittest.TestCase):
    def setUp(self):
        """테스트 실행 전 설정"""
        self.manager = GoogleSheetsManager(credentials_file="test_credentials.json")
        
    def test_init(self):
        """초기화 테스트"""
        self.assertEqual(self.manager.credentials_file, "test_credentials.json")
        self.assertIsNone(self.manager.client)
        self.assertIsNone(self.manager.sheet)
        self.assertTrue(os.path.exists(self.manager.data_dir))
    
    @patch('gspread.authorize')
    @patch('oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name')
    def test_authenticate(self, mock_credentials, mock_authorize):
        """인증 테스트"""
        # Mock 설정
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client
        
        # 테스트 실행
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            result = self.manager.authenticate()
        
        self.assertTrue(result)
        self.assertEqual(self.manager.client, mock_client)
        mock_credentials.assert_called_once()
        mock_authorize.assert_called_once()
    
    @patch('gspread.authorize')
    @patch('oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name')
    def test_authenticate_file_not_found(self, mock_credentials, mock_authorize):
        """인증 파일 없을 때 테스트"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            result = self.manager.authenticate()
        
        self.assertFalse(result)
        self.assertIsNone(self.manager.client)
    
    def test_open_spreadsheet(self):
        """스프레드시트 열기 테스트"""
        # Mock 클라이언트 설정
        mock_client = MagicMock()
        mock_sheet = MagicMock()
        mock_sheet.title = "Test Sheet"
        mock_client.open_by_key.return_value = mock_sheet
        self.manager.client = mock_client
        
        # 테스트 실행
        result = self.manager.open_spreadsheet(spreadsheet_id="test_id")
        
        self.assertTrue(result)
        self.assertEqual(self.manager.sheet, mock_sheet)
        mock_client.open_by_key.assert_called_once_with("test_id")
    
    def test_get_or_create_worksheet(self):
        """워크시트 생성/가져오기 테스트"""
        # Mock 시트 설정
        mock_sheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_sheet.worksheet.return_value = mock_worksheet
        self.manager.sheet = mock_sheet
        
        # 테스트 실행
        result = self.manager.get_or_create_worksheet("Test")
        
        self.assertEqual(result, mock_worksheet)
        mock_sheet.worksheet.assert_called_once_with("Test")
    
    def test_save_news_to_sheet(self):
        """뉴스 데이터 저장 테스트"""
        # Mock 설정
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [["header1", "header2"]]
        
        self.manager.authenticate = MagicMock(return_value=True)
        self.manager.open_spreadsheet = MagicMock(return_value=True)
        self.manager.get_or_create_worksheet = MagicMock(return_value=mock_worksheet)
        
        # 테스트 데이터
        test_news = [{
            'date': '2024-03-29',
            'title': 'Test News',
            'source': 'Test Source',
            'content': 'Test Content',
            'url': 'http://test.com'
        }]
        
        # 테스트 실행
        result = self.manager.save_news_to_sheet(test_news, "Test Sheet")
        
        self.assertTrue(result)
        mock_worksheet.update.assert_called()
        self.manager.get_or_create_worksheet.assert_called_once_with("Test Sheet")
    
    def test_save_news_to_sheet_twitter(self):
        """트위터 데이터 저장 테스트"""
        # Mock 설정
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [["header1", "header2"]]
        
        self.manager.authenticate = MagicMock(return_value=True)
        self.manager.open_spreadsheet = MagicMock(return_value=True)
        self.manager.get_or_create_worksheet = MagicMock(return_value=mock_worksheet)
        
        # 테스트 데이터
        test_news = [{
            'tweet_text': 'Test Tweet',
            'created_at': 'Wed Mar 29 12:00:00 +0000 2024',
            'title': 'Test Tweet Title',
            'tweet_url': 'http://twitter.com/test'
        }]
        
        # 테스트 실행
        result = self.manager.save_news_to_sheet(test_news, "Test Sheet")
        
        self.assertTrue(result)
        mock_worksheet.update.assert_called()
        self.manager.get_or_create_worksheet.assert_called_once_with("Test Sheet")

if __name__ == '__main__':
    unittest.main() 