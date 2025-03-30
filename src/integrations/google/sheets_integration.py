#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
구글 시트 연동 모듈 - 크롤링된 뉴스 데이터를 구글 시트에 저장
"""

import os
import sys
import json
import datetime
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

class GoogleSheetsManager:
    """크롤링된 뉴스 데이터를 구글 시트에 저장하는 클래스"""
    
    def __init__(self, credentials_file=None):
        """초기화 함수
        
        Args:
            credentials_file (str, optional): 구글 API 인증 정보 파일 경로
        """
        # 환경 변수 다시 로드
        load_dotenv()
        
        # 인증 정보 파일 경로 설정
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE')
        
        # 구글 시트 ID 설정
        self.spreadsheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        # 서비스 계정 이메일 설정
        self.service_account_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
        
        # 데이터 디렉토리 설정 및 생성
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 구글 시트 클라이언트 초기화
        self.client = None
        self.sheet = None
        
        print(f"초기화 - 시트 ID: {self.spreadsheet_id}")
        print(f"초기화 - 서비스 계정: {self.service_account_email}")
    
    def authenticate(self):
        """구글 API 인증
        
        Returns:
            bool: 인증 성공 여부
        """
        try:
            # 인증 정보 파일 확인
            if not self.credentials_file or not os.path.exists(self.credentials_file):
                logger.error(f"구글 API 인증 정보 파일을 찾을 수 없습니다: {self.credentials_file}")
                return False
            
            # API 범위 설정
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 인증 정보 로드
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
            
            # 구글 시트 클라이언트 생성
            self.client = gspread.authorize(credentials)
            
            # 클라이언트 테스트
            try:
                # 테스트용 시트 생성 시도
                test_sheet = self.client.create('Test Sheet')
                # 테스트 성공 시 시트 삭제
                self.client.del_spreadsheet(test_sheet.id)
                logger.info("구글 API 인증 성공")
                return True
            except Exception as e:
                logger.error(f"구글 API 테스트 중 오류 발생: {e}")
                return False
            
        except Exception as e:
            logger.error(f"구글 API 인증 중 오류 발생: {e}")
            return False
    
    def open_spreadsheet(self, spreadsheet_id=None):
        """구글 시트를 열거나 생성합니다."""
        try:
            # 기존 시트 ID가 있으면 해당 시트를 엽니다
            sheet_id = spreadsheet_id or self.spreadsheet_id
            logger.info(f"구글 sheet_id: {sheet_id}")
            if sheet_id:
                try:
                    self.sheet = self.client.open_by_key(sheet_id)
                    logger.info(f"구글 시트 열기 성공: {self.sheet.title}")
                    return True
                except Exception as e:
                    logger.warning(f"기존 시트 열기 실패: {str(e)}")
                    return False
            
            # 시트 ID가 없는 경우 새로 생성
            title = f"AI 뉴스 데이터 {datetime.datetime.now().strftime('%Y-%m-%d')}"
            self.sheet = self.client.create(title)
            
            # 시트 공유 설정
            self.sheet.share(
                email_address=self.service_account_email,
                perm_type='user',
                role='writer',
                notify=False
            )
            
            logger.info(f"새 구글 시트 생성 성공: {title} (ID: {self.sheet.id})")
            return True
            
        except Exception as e:
            logger.error(f"새 구글 시트 생성 중 오류 발생: {str(e)}")
            return False
    
    def get_or_create_worksheet(self, title):
        """워크시트 가져오기 또는 생성
        
        Args:
            title (str): 워크시트 제목
            
        Returns:
            gspread.Worksheet: 워크시트 객체
        """
        try:
            # 워크시트 가져오기 시도
            try:
                worksheet = self.sheet.worksheet(title)
                logger.info(f"기존 워크시트 열기 성공: {title}")
            except gspread.exceptions.WorksheetNotFound:
                # 워크시트가 없을 경우 새로 생성
                worksheet = self.sheet.add_worksheet(title=title, rows=1000, cols=20)
                logger.info(f"새 워크시트 생성 성공: {title}")
            
            return worksheet
        
        except Exception as e:
            logger.error(f"워크시트 가져오기/생성 중 오류 발생: {e}")
            return None
    
    def clear_worksheet(self, worksheet):
        """워크시트의 모든 데이터 삭제
        
        Args:
            worksheet: 초기화할 워크시트 객체
            
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            # 워크시트의 모든 데이터 가져오기
            all_values = worksheet.get_all_values()
            if not all_values:
                return True
            
            # 데이터가 있는 범위 계산
            num_rows = len(all_values)
            num_cols = len(all_values[0]) if all_values else 0
            
            if num_rows > 0 and num_cols > 0:
                # 모든 데이터 삭제
                range_str = f'A1:{chr(64 + num_cols)}{num_rows}'
                worksheet.clear()
                logger.info(f"워크시트 초기화 완료: {range_str}")
            
            return True
            
        except Exception as e:
            logger.error(f"워크시트 초기화 중 오류 발생: {e}")
            return False

    def save_news_to_sheet(self, news_data, worksheet_title=None):
        """뉴스 데이터를 구글 시트에 저장
        
        Args:
            news_data (list): 저장할 뉴스 데이터
            worksheet_title (str, optional): 워크시트 제목
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # 인증 확인
            if not self.client:
                if not self.authenticate():
                    return False
            
            # 구글 시트 열기
            if not self.sheet:
                if not self.open_spreadsheet():
                    return False
            
            # 워크시트 제목 설정 (기본값: 'AI_뉴스_데이터')
            if not worksheet_title:
                worksheet_title = "AI_뉴스_데이터"
            
            # 워크시트 가져오기 또는 생성
            worksheet = self.get_or_create_worksheet(worksheet_title)
            
            if not worksheet:
                return False
            
            # 현재 데이터 확인
            current_data = worksheet.get_all_values()
            
            # 헤더가 없는 경우에만 헤더 추가
            headers = ["날짜", "제목", "출처", "내용", "URL", "수집 시간"]
            if not current_data:
                worksheet.update('A1:F1', [headers])
                start_row = 2
            else:
                # 헤더 확인 및 업데이트
                if current_data[0] != headers:
                    worksheet.update('A1:F1', [headers])
                start_row = len(current_data) + 1
            
            # 데이터 준비
            rows = []
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for news in news_data:
                row = []
                
                # Twitter 형식 데이터 처리
                if 'tweet_text' in news:
                    # 날짜 처리
                    created_at = news.get('created_at', current_time)
                    if isinstance(created_at, str):
                        try:
                            # Twitter 날짜 형식 변환 시도
                            date_obj = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
                            date_str = date_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            # 다른 형식 시도
                            try:
                                date_obj = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                                date_str = date_obj.strftime('%Y-%m-%d')
                            except ValueError:
                                date_str = created_at
                    else:
                        date_str = current_time.split()[0]
                    
                    row = [
                        date_str,  # 날짜
                        news.get('title', ''),  # 제목
                        'Twitter',  # 출처
                        news.get('tweet_text', ''),  # 내용
                        news.get('tweet_url', ''),  # URL
                        current_time  # 수집 시간
                    ]
                
                # 일반 뉴스 데이터 처리
                else:
                    row = [
                        news.get('date', current_time.split()[0]),  # 날짜
                        news.get('title', ''),  # 제목
                        news.get('source', ''),  # 출처
                        news.get('content', ''),  # 내용
                        news.get('url', ''),  # URL
                        current_time  # 수집 시간
                    ]
                
                rows.append(row)
            
            # 데이터가 있는 경우에만 업데이트
            if rows:
                # 새 데이터 추가
                range_str = f'A{start_row}:F{start_row + len(rows) - 1}'
                worksheet.update(range_str, rows)
                
                logger.info(f"{len(rows)}개의 뉴스 데이터를 시트에 추가했습니다. (전체: {start_row + len(rows) - 1}개)")
                return True
            else:
                logger.warning("저장할 뉴스 데이터가 없습니다.")
                return False
        
        except Exception as e:
            logger.error(f"뉴스 데이터 저장 중 오류 발생: {e}")
            return False 