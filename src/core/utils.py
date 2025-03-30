#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
공통 유틸리티 함수 모듈
"""

import os
import json
import datetime
from typing import Dict, Any, Optional

def save_metadata(filepath: str, metadata: Dict[str, Any], metadata_dir: str) -> Optional[str]:
    """메타데이터 저장
    
    Args:
        filepath (str): 원본 파일 경로
        metadata (dict): 저장할 메타데이터
        metadata_dir (str): 메타데이터 저장 디렉토리
        
    Returns:
        Optional[str]: 저장된 메타데이터 파일 경로 또는 None
    """
    try:
        # 기본 정보 추가
        metadata.update({
            'original_path': filepath,
            'filename': os.path.basename(filepath),
            'created_at': datetime.datetime.now().isoformat()
        })
        
        # 메타데이터 파일 경로
        filename = os.path.basename(filepath)
        metadata_filename = f"{os.path.splitext(filename)[0]}_metadata.json"
        metadata_path = os.path.join(metadata_dir, metadata_filename)
        
        # 메타데이터 저장
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return metadata_path
        
    except Exception as e:
        print(f"메타데이터 저장 중 오류 발생: {e}")
        return None

def load_metadata(filepath: str, metadata_dir: str) -> Optional[Dict[str, Any]]:
    """메타데이터 로드
    
    Args:
        filepath (str): 원본 파일 경로
        metadata_dir (str): 메타데이터 저장 디렉토리
        
    Returns:
        Optional[Dict[str, Any]]: 로드된 메타데이터 또는 None
    """
    try:
        # 메타데이터 파일 경로
        filename = os.path.basename(filepath)
        metadata_filename = f"{os.path.splitext(filename)[0]}_metadata.json"
        metadata_path = os.path.join(metadata_dir, metadata_filename)
        
        # 메타데이터 파일이 존재하는 경우에만 로드
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
        
    except Exception as e:
        print(f"메타데이터 로드 중 오류 발생: {e}")
        return None

def get_latest_file(directory: str, prefix: str = '', suffix: str = '') -> Optional[str]:
    """가장 최근에 생성된 파일 찾기
    
    Args:
        directory (str): 검색할 디렉토리
        prefix (str): 파일명 접두사
        suffix (str): 파일명 접미사
        
    Returns:
        Optional[str]: 가장 최근 파일의 경로 또는 None
    """
    try:
        # 디렉토리 내 파일 목록 필터링
        files = [f for f in os.listdir(directory) 
                if f.startswith(prefix) and f.endswith(suffix)]
        
        if not files:
            return None
        
        # 최근 파일 선택 (파일명 기준 정렬)
        latest_file = sorted(files)[-1]
        return os.path.join(directory, latest_file)
        
    except Exception as e:
        print(f"최근 파일 검색 중 오류 발생: {e}")
        return None

def format_filename(base: str, index: Optional[int] = None, timestamp: bool = True) -> str:
    """파일명 포맷팅
    
    Args:
        base (str): 기본 파일명
        index (int, optional): 인덱스 번호
        timestamp (bool): 타임스탬프 포함 여부
        
    Returns:
        str: 포맷팅된 파일명
    """
    parts = [base]
    
    if index is not None:
        parts.append(str(index))
    
    if timestamp:
        parts.append(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    
    return '_'.join(parts) 