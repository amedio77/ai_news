#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RSS 피드를 활용한 AI 관련 뉴스 크롤러
"""

import os
import sys
import json
import time
import datetime
import requests
import re
import logging
import hashlib
from bs4 import BeautifulSoup
import feedparser
from newspaper import Article
from newspaper.article import ArticleException
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple, Any
import pytz

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RSSNewsCrawler:
    """RSS 피드를 활용하여 AI 관련 뉴스를 수집하는 클래스"""
    
    def __init__(self):
        """초기화 함수"""
        # 프로젝트 루트 디렉토리 설정
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 설정 디렉토리 설정
        self.config_dir = os.path.join(self.root_dir, 'config')
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # 데이터 디렉토리 설정
        self.data_dir = os.path.join(self.root_dir, 'data')
        self.crawled_dir = os.path.join(self.data_dir, 'crawled')
        self.metrics_dir = os.path.join(self.data_dir, 'metrics')
        
        # 필요한 디렉토리가 없으면 생성
        for directory in [self.data_dir, self.crawled_dir, self.metrics_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # RSS 피드 설정 파일 경로
        self.feeds_file = os.path.join(self.config_dir, 'rss_feeds.json')
        
        # 성능 메트릭 저장 파일
        self.metrics_file = os.path.join(self.metrics_dir, 'feed_metrics.json')
        
        # 중복 체크를 위한 해시 저장소
        self.hash_file = os.path.join(self.metrics_dir, 'news_hashes.json')
        
        # RSS 피드 로드
        self.rss_feeds = self._load_feeds()
        
        # 성능 메트릭 로드
        self.feed_metrics = self._load_metrics()
        
        # 뉴스 해시 로드
        self.news_hashes = self._load_hashes()
        
        # 재시도 설정
        self.max_retries = 3
        self.retry_delay = 5  # 초
        
        # 타임아웃 설정
        self.timeout = 30  # 초
        
        # 동시 처리 설정
        self.max_workers = 10
        
        # HTTP 요청 헤더
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        # AI 관련 키워드 설정
        self.ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning', 
            'neural network', 'gpt', 'llm', 'large language model', 'chatgpt',
            'generative ai', 'computer vision', 'nlp', 'natural language processing',
            'transformer', 'openai', 'anthropic', 'claude', 'gemini', 'mistral',
            '인공지능', '머신러닝', '딥러닝', '신경망', '생성형 AI'
        ]
        
        # 제외할 키워드 설정
        self.exclude_keywords = [
            'air', 'airpods', 'macbook air',  # Apple 제품명에서 'air'가 들어가는 경우 제외
            'carplay', 'android auto', 'car display', 'entertainment system',  # 차량 엔터테인먼트 시스템 관련
            'stock', 'price', 'market', 'shares', 'trading', 'investor',  # 주가 관련 키워드
            '주가', '주식', '시장', '투자'  # 주가 관련 키워드
        ]
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.2365.92',
        ]
        self.current_user_agent = 0

    def _load_feeds(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """RSS 피드 설정 로드"""
        try:
            if os.path.exists(self.feeds_file):
                with open(self.feeds_file, 'r', encoding='utf-8') as f:
                    feeds = json.load(f)
                logger.info(f"Loaded {sum(len(category) for category in feeds.values())} feeds from {self.feeds_file}")
                return feeds
            else:
                logger.warning(f"Feed configuration file not found: {self.feeds_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading feeds: {e}")
            return {}

    def _save_feeds(self):
        """RSS 피드 설정 저장"""
        try:
            with open(self.feeds_file, 'w', encoding='utf-8') as f:
                json.dump(self.rss_feeds, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved feed configuration to {self.feeds_file}")
        except Exception as e:
            logger.error(f"Error saving feeds: {e}")

    def add_feed(self, name: str, url: str, category: str = 'general', feed_type: str = 'tech',
                language: str = 'en', update_frequency: str = 'daily'):
        """새로운 RSS 피드 추가"""
        if category not in self.rss_feeds:
            self.rss_feeds[category] = {}
        
        self.rss_feeds[category][name] = {
            'url': url,
            'category': feed_type,
            'language': language,
            'update_frequency': update_frequency
        }
        
        self._save_feeds()
        logger.info(f"Added new feed: {name} ({url}) to category {category}")

    def remove_feed(self, name: str, category: str = None):
        """RSS 피드 제거"""
        if category and category in self.rss_feeds and name in self.rss_feeds[category]:
            del self.rss_feeds[category][name]
            self._save_feeds()
            logger.info(f"Removed feed: {name} from category {category}")
        else:
            # 모든 카테고리에서 검색
            for cat in self.rss_feeds:
                if name in self.rss_feeds[cat]:
                    del self.rss_feeds[cat][name]
                    self._save_feeds()
                    logger.info(f"Removed feed: {name} from category {cat}")
                    return
            logger.warning(f"Feed not found: {name}")

    def update_feed(self, name: str, category: str, **kwargs):
        """RSS 피드 정보 업데이트"""
        if category in self.rss_feeds and name in self.rss_feeds[category]:
            self.rss_feeds[category][name].update(kwargs)
            self._save_feeds()
            logger.info(f"Updated feed: {name} in category {category}")
        else:
            logger.warning(f"Feed not found: {name} in category {category}")

    def get_full_article_content(self, url):
        """Newspaper3k를 사용하여 전체 기사 내용 가져오기"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            # 기사 정보 추출
            content = article.text
            authors = article.authors
            publish_date = article.publish_date
            top_image = article.top_image
            
            return {
                'content': content,
                'authors': authors,
                'publish_date': publish_date.strftime('%Y-%m-%d %H:%M:%S') if publish_date else None,
                'top_image': top_image
            }
        except ArticleException as e:
            logger.warning(f"Failed to fetch article content from {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while fetching article from {url}: {e}")
            return None
    
    def _crawl_single_feed(self, feed_name: str, feed_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """단일 RSS 피드 크롤링

        Args:
            feed_name (str): 피드 이름
            feed_info (Dict[str, Any]): 피드 정보 (URL, 카테고리, 언어 등)

        Returns:
            List[Dict[str, Any]]: 수집된 뉴스 항목 리스트
        """
        headers = {'User-Agent': self._get_next_user_agent()}
        start_time = time.time()
        success = False
        news_items = []

        feed_url = feed_info['url']
        feed_language = feed_info['language']
        feed_category = feed_info['category']

        for attempt in range(self.max_retries):
            try:
                response = requests.get(feed_url, headers=headers, timeout=self.timeout, allow_redirects=True)
                response.raise_for_status()
                feed = feedparser.parse(response.content)
                
                if feed.entries:
                    for entry in feed.entries:
                        news_item = self._process_entry(entry, feed_name)
                        if news_item:
                            # 피드 메타데이터 추가
                            news_item.update({
                                'feed_language': feed_language,
                                'feed_category': feed_category
                            })
                            news_items.append(news_item)
                    success = True
                    break
                else:
                    logging.warning(f"No entries found in feed: {feed_name}")
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Attempt {attempt + 1} timed out for {feed_name}")
            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed for {feed_name}: {str(e)}")
            except Exception as e:
                logging.error(f"Unexpected error processing {feed_name}: {str(e)}")
                break

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)

        end_time = time.time()
        self._update_feed_metrics(feed_name, success, end_time - start_time)
        return news_items
    
    def _process_entry(self, entry: Dict[str, Any], feed_name: str) -> Optional[Dict[str, Any]]:
        """Process a single feed entry."""
        try:
            # Get published date
            date_str = entry.get('published', entry.get('updated', ''))
            if not date_str:
                self.logger.warning(f"No date found for entry from {feed_name}")
                return None

            # Parse date
            published_date = self._parse_date(date_str)
            
            # Get yesterday's date range
            start_date, end_date = self._get_yesterday_range()
            
            # Check if the entry is within yesterday's date range
            if not self._is_within_date_range(published_date, start_date, end_date):
                return None

            # Get title and description
            title = entry.get('title', '').strip()
            description = entry.get('description', entry.get('summary', '')).strip()

            # Skip if no title or description
            if not title or not description:
                self.logger.warning(f"Missing title or description for entry from {feed_name}")
                return None

            # Check for AI-related keywords in title or description
            if not (self._contains_ai_keywords(title) or self._contains_ai_keywords(description)):
                return None

            # Check for excluded keywords
            if self._contains_exclude_keywords(title) or self._contains_exclude_keywords(description):
                return None

            # Get link
            link = entry.get('link', '')
            if not link:
                self.logger.warning(f"No link found for entry from {feed_name}")
                return None

            # Create news item
            news_item = {
                'title': title,
                'description': description,
                'link': link,
                'published': published_date.isoformat(),
                'source': feed_name
            }

            return news_item

        except Exception as e:
            self.logger.error(f"Error processing entry from {feed_name}: {str(e)}")
            return None
    
    def _validate_and_update_feed(self, feed_name: str, feed_info: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """RSS 피드 URL 검증 및 업데이트
        
        Args:
            feed_name (str): 피드 이름
            feed_info (Dict[str, Any]): 피드 정보

        Returns:
            Tuple[bool, Optional[str]]: (유효성 여부, 업데이트된 URL)
        """
        try:
            feed_url = feed_info['url']
            if not feed_url.startswith(('http://', 'https://')):
                logger.warning(f"Invalid URL format for {feed_name}: {feed_url}")
                return False, None

            headers = {'User-Agent': self._get_next_user_agent()}
            response = requests.head(feed_url, headers=headers, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code == 200:
                if response.url != feed_url:
                    logger.info(f"Feed URL redirected: {feed_name} - {feed_url} -> {response.url}")
                    return True, response.url
                return True, None
            else:
                logger.warning(f"Feed URL returned status code {response.status_code}: {feed_name} - {feed_url}")
                return False, None
                
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout while validating {feed_name}")
            return False, None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error while validating {feed_name}: {str(e)}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error while validating {feed_name}: {str(e)}")
            return False, None

    def validate_and_update_feeds(self) -> Dict[str, Dict[str, List[str]]]:
        """모든 RSS 피드 URL 검증 및 업데이트

        Returns:
            Dict[str, Dict[str, List[str]]]: 검증 결과 보고서
        """
        validation_report = {
            'valid': {category: [] for category in self.rss_feeds},
            'invalid': {category: [] for category in self.rss_feeds},
            'updated': {category: [] for category in self.rss_feeds}
        }

        for category, feeds in self.rss_feeds.items():
            for feed_name, feed_info in feeds.items():
                is_valid, updated_url = self._validate_and_update_feed(feed_name, feed_info)
                
                if is_valid:
                    validation_report['valid'][category].append(feed_name)
                    if updated_url:
                        feed_info['url'] = updated_url
                        validation_report['updated'][category].append(feed_name)
                else:
                    validation_report['invalid'][category].append(feed_name)

        # 업데이트된 URL이 있으면 설정 파일 저장
        if any(len(updated) > 0 for updated in validation_report['updated'].values()):
            self._save_feeds()

        return validation_report

    def crawl_rss_feeds(self, feed_type: str = 'general', max_items_per_feed: int = None) -> List[Dict[str, Any]]:
        """RSS 피드 크롤링

        Args:
            feed_type (str): 크롤링할 피드 유형 ('all', 'general', 'specialized', 'korean')
            max_items_per_feed (int, optional): 각 피드당 최대 수집 항목 수
            
        Returns:
            List[Dict[str, Any]]: 수집된 뉴스 항목 리스트
        """
        # 피드 URL 검증 및 업데이트
        validation_report = self.validate_and_update_feeds()
        
        all_entries = []
        yesterday_start, yesterday_end = self._get_yesterday_range()
        logger.info(f"어제 날짜 범위: {yesterday_start} ~ {yesterday_end}")
        
        # 크롤링할 피드 선택 (유효한 피드만)
        feeds_to_crawl = []
        if feed_type == 'all':
            for category in ['general', 'specialized', 'korean']:
                if category in self.rss_feeds:
                    feeds_to_crawl.extend([
                        (name, info) for name, info in self.rss_feeds[category].items()
                        if name in validation_report['valid'][category]
                    ])
        elif feed_type in self.rss_feeds:
            feeds_to_crawl.extend([
                (name, info) for name, info in self.rss_feeds[feed_type].items()
                if name in validation_report['valid'][feed_type]
            ])
        else:
            logger.warning(f"Unknown feed type: {feed_type}, using 'general' instead")
            if 'general' in self.rss_feeds:
                feeds_to_crawl.extend([
                    (name, info) for name, info in self.rss_feeds['general'].items()
                    if name in validation_report['valid']['general']
                ])

        # 병렬 처리로 피드 크롤링
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_feed = {
                executor.submit(self._crawl_single_feed, name, info): (name, info)
                for name, info in feeds_to_crawl
            }
            
            for future in as_completed(future_to_feed):
                feed_name, feed_info = future_to_feed[future]
                try:
                    entries = future.result()
                    if max_items_per_feed and len(entries) > max_items_per_feed:
                        entries = entries[:max_items_per_feed]
                    all_entries.extend(entries)
            except Exception as e:
                logger.error(f"Error crawling {feed_name}: {e}")
        
        # 발행일 기준으로 정렬 (최신순)
        all_entries.sort(key=lambda x: x['published'], reverse=True)
        
        # 메트릭과 해시 저장
        self._save_metrics()
        self._save_hashes()
        
        logger.info(f"Total news items collected: {len(all_entries)}")
        return all_entries
    
    def save_news_data(self, news_data: List[Dict[str, Any]], filename: str = None) -> str:
        """뉴스 데이터를 JSON 파일로 저장
        
        Args:
            news_data (List[Dict[str, Any]]): 저장할 뉴스 데이터
            filename (str, optional): 저장할 파일명. 기본값은 None.
            
        Returns:
            str: 저장된 파일의 경로
        """
        if filename is None:
            # 파일명이 지정되지 않은 경우 현재 날짜로 파일명 생성
            filename = f"ai_news_rss_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        
        # 파일 경로 생성
        file_path = os.path.join(self.crawled_dir, filename)
        
        try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        logger.info(f"News data saved to {file_path}")
        return file_path
        except Exception as e:
            logger.error(f"Error saving news data: {str(e)}")
            return None
    
    def convert_to_twitter_format(self, news_data):
        """RSS 뉴스 데이터를 Twitter 크롤러 형식으로 변환 (호환성 유지)
        
        Args:
            news_data (list): RSS 형식의 뉴스 데이터
            
        Returns:
            list: Twitter 크롤러 형식의 뉴스 데이터
        """
        twitter_format_data = []
        
        for item in news_data:
            # Twitter 형식으로 변환
            twitter_item = {
                'user_name': item['source'],
                'user_screen_name': item['source'].replace(' ', '_').lower(),
                'tweet_text': f"{item['title']}\n\n{item['description']}\n\n{item['link']}",
                'created_at': item['published'],
                'source_type': 'rss'
            }
            
            twitter_format_data.append(twitter_item)
        
        return twitter_format_data
    
    def crawl_and_save(self, feed_type='all', max_items_per_feed=5, convert_format=True):
        """뉴스 크롤링 및 저장 통합 함수
        
        Args:
            feed_type (str): 수집할 피드 유형 ('all', 'general', 'specialized')
            max_items_per_feed (int): 각 피드에서 수집할 최대 항목 수
            convert_format (bool): Twitter 형식으로 변환 여부
            
        Returns:
            tuple: (저장된 파일 경로, 수집된 뉴스 데이터)
        """
        # RSS 피드에서 뉴스 수집
        news_data = self.crawl_rss_feeds(feed_type, max_items_per_feed)
        
        # 형식 변환 (필요시)
        if convert_format:
            news_data = self.convert_to_twitter_format(news_data)
        
        # 현재 날짜 기반 파일명 생성
        current_date = datetime.datetime.now().strftime('%Y%m%d')
        filename = f"ai_news_rss_{current_date}.json"
        
        # 데이터 저장
        file_path = self.save_news_data(news_data, filename)
        
        return file_path, news_data

    def _load_metrics(self) -> Dict[str, Dict[str, Any]]:
        """성능 메트릭 로드"""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metrics: {e}")
        return {}
    
    def _save_metrics(self):
        """성능 메트릭 저장"""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.feed_metrics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def _load_hashes(self) -> Dict[str, str]:
        """뉴스 해시 로드"""
        if os.path.exists(self.hash_file):
            try:
                with open(self.hash_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading hashes: {e}")
        return {}
    
    def _save_hashes(self):
        """뉴스 해시 저장"""
        try:
            # 30일 이상 된 해시 제거
            current_time = datetime.datetime.now()
            old_hashes = {
                k: v for k, v in self.news_hashes.items()
                if datetime.datetime.strptime(v['date'], '%Y-%m-%d') > current_time - datetime.timedelta(days=30)
            }
            
            with open(self.hash_file, 'w', encoding='utf-8') as f:
                json.dump(old_hashes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving hashes: {e}")
    
    def _generate_news_hash(self, news_item: Dict[str, Any]) -> str:
        """뉴스 항목의 해시 생성"""
        hash_string = f"{news_item['title']}{news_item['link']}{news_item['published']}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _is_duplicate(self, news_item: Dict[str, Any]) -> bool:
        """중복 뉴스 체크"""
        news_hash = self._generate_news_hash(news_item)
        is_duplicate = news_hash in self.news_hashes
        
        if not is_duplicate:
            self.news_hashes[news_hash] = {
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'title': news_item['title']
            }
        
        return is_duplicate
    
    def _update_feed_metrics(self, feed_name: str, success: bool, response_time: float):
        """피드 성능 메트릭 업데이트"""
        if feed_name not in self.feed_metrics:
            self.feed_metrics[feed_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_response_time': 0,
                'avg_response_time': 0,
                'last_success': None,
                'last_failure': None
            }
        
        metrics = self.feed_metrics[feed_name]
        metrics['total_requests'] += 1
        metrics['total_response_time'] += response_time
        metrics['avg_response_time'] = metrics['total_response_time'] / metrics['total_requests']
        
        if success:
            metrics['successful_requests'] += 1
            metrics['last_success'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            metrics['failed_requests'] += 1
            metrics['last_failure'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _get_next_user_agent(self):
        self.current_user_agent = (self.current_user_agent + 1) % len(self.user_agents)
        return self.user_agents[self.current_user_agent]

    def _get_yesterday_range(self) -> tuple[datetime, datetime]:
        """Get the start and end time for yesterday."""
        utc = pytz.UTC
        now = datetime.datetime.now(utc)
        yesterday = now - datetime.timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        utc = pytz.UTC
        try:
            # Try parsing with feedparser's date parser
            parsed_date = feedparser._parse_date(date_str)
            if parsed_date:
                # Convert to datetime object with UTC timezone
                dt = datetime.datetime(*parsed_date[:6])
                return utc.localize(dt) if dt.tzinfo is None else dt.astimezone(utc)
        except Exception:
            pass

        try:
            # Try common date formats
            for fmt in [
                '%Y-%m-%dT%H:%M:%S%z',  # ISO format with timezone
                '%Y-%m-%d %H:%M:%S%z',
                '%a, %d %b %Y %H:%M:%S %z',  # RFC 822
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d',
            ]:
                try:
                    dt = datetime.datetime.strptime(date_str, fmt)
                    return utc.localize(dt) if dt.tzinfo is None else dt.astimezone(utc)
                except ValueError:
                    continue
        except Exception as e:
            self.logger.warning(f"Error parsing date {date_str}: {str(e)}")
        
        # If all parsing attempts fail, return current time
        return datetime.datetime.now(utc)

    def _is_within_date_range(self, date: datetime, start: datetime, end: datetime) -> bool:
        """Check if date is within the given range."""
        utc = pytz.UTC
        if date.tzinfo is None:
            date = utc.localize(date)
        return start <= date <= end

    def _contains_ai_keywords(self, text: str) -> bool:
        """텍스트에 AI 관련 키워드가 포함되어 있는지 확인"""
        text = text.lower()
        return any(keyword.lower() in text for keyword in self.ai_keywords)

    def _contains_exclude_keywords(self, text: str) -> bool:
        """텍스트에 제외할 키워드가 포함되어 있는지 확인"""
        text = text.lower()
        return any(keyword.lower() in text for keyword in self.exclude_keywords)

def main():
    """메인 함수"""
    crawler = RSSNewsCrawler()
    
    # 명령행 인자 처리
    import argparse
    parser = argparse.ArgumentParser(description='RSS 피드에서 AI 관련 뉴스 수집')
    parser.add_argument('--type', choices=['all', 'general', 'specialized'], default='all',
                        help='수집할 피드 유형 (기본값: all)')
    parser.add_argument('--max', type=int, default=5,
                        help='각 피드에서 수집할 최대 항목 수 (기본값: 5)')
    parser.add_argument('--format', choices=['rss', 'twitter'], default='twitter',
                        help='저장 형식 (기본값: twitter)')
    
    args = parser.parse_args()
    
    # 뉴스 크롤링 및 저장
    convert_format = (args.format == 'twitter')
    file_path, news_data = crawler.crawl_and_save(args.type, args.max, convert_format)
    
    print(f"수집된 뉴스 항목: {len(news_data)}개")
    print(f"저장된 파일 경로: {file_path}")

if __name__ == "__main__":
    main()
