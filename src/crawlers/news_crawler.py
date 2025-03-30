#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
뉴스 크롤링 모듈
"""

import os
import json
import datetime
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsCrawler:
    """뉴스 크롤러 클래스"""
    
    def __init__(self):
        """초기화 함수"""
        # User-Agent 설정
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        
        # 크롤링 대상 뉴스 사이트 설정
        self.news_sites = {
            'zdnet': {
                'name': 'ZDNet Korea',
                'url': 'https://zdnet.co.kr/news/',
                'article_selector': 'div.article_list article',
                'title_selector': 'h2.title > a',
                'link_selector': 'h2.title > a',
                'content_selector': 'p.summary'
            },
            'aitimes': {
                'name': 'AI Times',
                'url': 'https://www.aitimes.com/news/articleList.html?sc_section_code=S1N1',
                'article_selector': 'section.article-list-content',
                'title_selector': 'div.list-titles a',
                'link_selector': 'div.list-titles a',
                'content_selector': 'div.list-summary'
            }
        }
    
    def crawl_news(self, site_key: str) -> List[Dict]:
        """특정 사이트의 뉴스 크롤링
        
        Args:
            site_key (str): 크롤링할 사이트 키
            
        Returns:
            List[Dict]: 크롤링된 뉴스 데이터 리스트
        """
        try:
            if site_key not in self.news_sites:
                logger.error(f"지원하지 않는 뉴스 사이트입니다: {site_key}")
                return []
            
            site_info = self.news_sites[site_key]
            news_list = []
            
            # 뉴스 목록 페이지 가져오기
            try:
                response = requests.get(site_info['url'], headers=self.headers, timeout=10)
                response.raise_for_status()  # HTTP 에러 발생시 예외 발생
            except requests.RequestException as e:
                logger.error(f"페이지 요청 중 오류 발생: {str(e)}")
                return []
            
            logger.debug(f"HTTP 응답 코드: {response.status_code}")
            logger.debug(f"응답 헤더: {response.headers}")
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select(site_info['article_selector'])
            logger.debug(f"찾은 기사 수: {len(articles)}")
            
            if not articles:
                logger.warning(f"기사를 찾을 수 없습니다. 셀렉터: {site_info['article_selector']}")
                logger.debug(f"페이지 내용 일부: {soup.prettify()[:500]}...")
                return []
            
            for article in articles:
                try:
                    # 제목과 링크 추출
                    title_elem = article.select_one(site_info['title_selector'])
                    if not title_elem:
                        logger.warning("제목 요소를 찾을 수 없습니다")
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # 상대 URL을 절대 URL로 변환
                    if link:
                        if link.startswith('//'):
                            link = 'https:' + link
                        elif link.startswith('/'):
                            base_url = '/'.join(site_info['url'].split('/')[:3])  # http(s)://domain.com
                            link = base_url + link
                        logger.debug(f"처리된 URL: {link}")
                    else:
                        logger.warning(f"링크를 찾을 수 없습니다: {title}")
                        continue
                    
                    # 내용 추출
                    content_elem = article.select_one(site_info['content_selector'])
                    if content_elem:
                        content = content_elem.get_text(strip=True)
                        logger.debug(f"내용 추출 성공: {content[:50]}...")
                    else:
                        content = ""
                        logger.warning(f"내용을 찾을 수 없습니다: {title}")
                    
                    # 뉴스 데이터 저장
                    news_data = {
                        'title': title,
                        'content': content,
                        'url': link,
                        'source': site_info['name'],
                        'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    news_list.append(news_data)
                    logger.debug(f"기사 추가됨: {title}")
                    
                except Exception as e:
                    logger.error(f"기사 파싱 중 오류 발생: {str(e)}")
                    continue
            
            logger.info(f"{site_key}에서 {len(news_list)}개의 뉴스를 크롤링했습니다.")
            return news_list
            
        except Exception as e:
            logger.error(f"뉴스 크롤링 중 오류 발생: {str(e)}")
            return []
    
    def crawl_all_news(self) -> List[Dict]:
        """모든 뉴스 사이트 크롤링
        
        Returns:
            List[Dict]: 크롤링된 뉴스 데이터 리스트
        """
        all_news = []
        
        for site_key in self.news_sites:
            news_list = self.crawl_news(site_key)
            all_news.extend(news_list)
        
        return all_news
    
    def save_to_file(self, news_data: List[Dict], filename: str) -> bool:
        """크롤링된 뉴스를 파일로 저장
        
        Args:
            news_data (List[Dict]): 저장할 뉴스 데이터
            filename (str): 저장할 파일명
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"뉴스 데이터가 {filename}에 저장되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"뉴스 데이터 저장 중 오류 발생: {str(e)}")
            return False 