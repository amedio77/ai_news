#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
뉴스 크롤링 데이터 정제 모듈
"""

import os
import json
import re
from datetime import datetime

class NewsProcessor:
    """크롤링된 뉴스 데이터를 정제하는 클래스"""
    
    def __init__(self, input_file=None):
        """초기화 함수
        
        Args:
            input_file (str, optional): 입력 파일 경로
        """
        self.input_file = input_file
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        
        # 출력 디렉토리가 없으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_news_data(self, file_path=None):
        """뉴스 데이터 로드
        
        Args:
            file_path (str, optional): 로드할 파일 경로. 기본값은 초기화 시 지정된 파일.
            
        Returns:
            list: 로드된 뉴스 데이터
        """
        file_path = file_path or self.input_file
        
        if not file_path:
            print("파일 경로가 지정되지 않았습니다.")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            return news_data
        except Exception as e:
            print(f"뉴스 데이터 로드 중 오류 발생: {e}")
            return []
    
    def clean_tweet_text(self, text):
        """트윗 텍스트 정제
        
        Args:
            text (str): 정제할 트윗 텍스트
            
        Returns:
            str: 정제된 텍스트
        """
        # URL 제거
        text = re.sub(r'https?://\S+', '', text)
        
        # 해시태그 정리 (# 기호 제거하고 공백 추가)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # 멘션 제거
        text = re.sub(r'@\S+', '', text)
        
        # 여러 공백을 하나로 치환
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_urls(self, text):
        """텍스트에서 URL 추출
        
        Args:
            text (str): URL을 추출할 텍스트
            
        Returns:
            list: 추출된 URL 리스트
        """
        url_pattern = re.compile(r'https?://\S+')
        return url_pattern.findall(text)
    
    def process_news_data(self, news_data=None):
        """뉴스 데이터 처리
        
        Args:
            news_data (list, optional): 처리할 뉴스 데이터. 기본값은 로드된 데이터.
            
        Returns:
            list: 처리된 뉴스 데이터
        """
        if news_data is None:
            news_data = self.load_news_data()
        
        if not news_data:
            return []
        
        processed_data = []
        
        for item in news_data:
            # 원본 트윗 텍스트 저장
            original_text = item.get('tweet_text', '')
            
            # URL 추출
            urls = self.extract_urls(original_text)
            
            # 텍스트 정제
            cleaned_text = self.clean_tweet_text(original_text)
            
            # 처리된 항목 생성
            processed_item = {
                'user_name': item.get('user_name', ''),
                'user_screen_name': item.get('user_screen_name', ''),
                'user_verified': item.get('user_verified', False),
                'original_text': original_text,
                'cleaned_text': cleaned_text,
                'urls': urls,
                'timestamp': item.get('timestamp', datetime.now().isoformat()),
                'source': 'Twitter'
            }
            
            processed_data.append(processed_item)
        
        return processed_data
    
    def save_processed_data(self, processed_data, filename=None):
        """처리된 데이터를 파일로 저장
        
        Args:
            processed_data (list): 저장할 처리된 데이터
            filename (str, optional): 저장할 파일명. 기본값은 현재 날짜 기반.
            
        Returns:
            str: 저장된 파일 경로
        """
        if not filename:
            current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"processed_ai_news_{current_date}.json"
        
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        print(f"처리된 뉴스 데이터가 {file_path}에 저장되었습니다.")
        return file_path

def main():
    """메인 함수"""
    # 가장 최근 크롤링된 파일 찾기
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    files = [f for f in os.listdir(data_dir) if f.startswith('ai_news_') and f.endswith('.json')]
    
    if not files:
        print("크롤링된 뉴스 파일을 찾을 수 없습니다.")
        return
    
    # 가장 최근 파일 선택 (파일명 기준 정렬)
    latest_file = sorted(files)[-1]
    input_file = os.path.join(data_dir, latest_file)
    
    processor = NewsProcessor(input_file)
    news_data = processor.load_news_data()
    
    if news_data:
        processed_data = processor.process_news_data(news_data)
        file_path = processor.save_processed_data(processed_data)
        print(f"총 {len(processed_data)}개의 뉴스 항목이 처리되었습니다.")
        print(f"처리된 데이터는 {file_path}에 저장되었습니다.")
    else:
        print("처리할 뉴스 데이터가 없습니다.")

if __name__ == "__main__":
    main()
