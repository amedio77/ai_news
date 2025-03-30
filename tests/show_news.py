#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
import html

def clean_text(text):
    """HTML 엔티티를 디코딩하고 텍스트를 정리"""
    # HTML 엔티티 디코딩
    text = html.unescape(text)
    # 여러 줄의 공백을 하나로
    text = ' '.join(text.split())
    return text

def extract_title_from_tweet(tweet_text):
    """트윗 텍스트에서 제목 추출"""
    lines = tweet_text.split('\n')
    return lines[0] if lines else 'No Title'

def show_news(filename):
    """수집된 뉴스를 보여주는 함수"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n총 {len(data)}개의 뉴스가 수집되었습니다.\n")
    print("수집된 뉴스 목록:")
    print("-" * 100)
    
    # 날짜순으로 정렬
    sorted_news = sorted(data, key=lambda x: x.get('created_at', ''), reverse=True)
    
    for item in sorted_news:
        # 시간 표시 형식 변경
        created_at = item.get('created_at', 'N/A')
        if created_at != 'N/A':
            dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            created_at = dt.strftime('%Y-%m-%d %H:%M')
        
        # 제목 추출
        if 'tweet_text' in item:
            title = extract_title_from_tweet(item['tweet_text'])
            content = clean_text(item['tweet_text'])
            # URL 추출
            url = content.split('https://')[-1].split()[0] if 'https://' in content else None
            # URL을 제외한 내용
            content = content.replace('https://' + url if url else '', '').strip()
        else:
            title = item.get('title', 'No Title')
            content = ''
            url = None
        
        print(f"[{created_at}] {title}")
        print(f"출처: {item.get('source', 'Unknown')}")
        if content:
            print("내용:")
            print(content)
        if url:
            print(f"링크: https://{url}")
        print("-" * 100)

if __name__ == "__main__":
    show_news('src/data/ai_news_rss_20250330.json') 