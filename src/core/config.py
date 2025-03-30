#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
프로젝트 설정 관리 모듈
"""

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class Config:
    """프로젝트 설정 클래스"""
    
    # 기본 디렉토리 설정
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    SRC_DIR = os.path.join(BASE_DIR, 'src')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    
    # 출력 디렉토리 설정
    BLOGS_DIR = os.path.join(OUTPUT_DIR, 'blogs')
    IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')
    METADATA_DIR = os.path.join(OUTPUT_DIR, 'metadata')
    
    # OpenAI API 설정
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # WordPress 설정
    WP_URL = os.getenv('WP_URL')
    WP_USERNAME = os.getenv('WP_USERNAME')
    WP_APP_PASSWORD = os.getenv('WP_APP_PASSWORD')
    WP_PASSWORD = os.getenv('WP_PASSWORD')
    
    # Google Sheets 설정
    GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    
    @classmethod
    def create_directories(cls):
        """필요한 디렉토리 생성"""
        directories = [
            cls.OUTPUT_DIR,
            cls.BLOGS_DIR,
            cls.IMAGES_DIR,
            cls.METADATA_DIR
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"디렉토리 생성: {directory}") 