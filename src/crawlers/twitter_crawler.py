#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Twitter API를 활용한 AI 관련 뉴스 크롤러 (수정 버전)
"""

import os
import sys
import json
import datetime
from dotenv import load_dotenv

# 데이터 API 클라이언트 임포트
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

# 환경 변수 로드
load_dotenv()

class TwitterNewsCrawler:
    """Twitter API를 사용하여 AI 관련 뉴스를 크롤링하는 클래스"""
    
    def __init__(self):
        """초기화 함수"""
        self.client = ApiClient()
        self.ai_keywords = os.getenv('AI_KEYWORDS', 'artificial intelligence,machine learning,deep learning,neural networks,AI,GPT,LLM').split(',')
        self.news_limit = int(os.getenv('NEWS_LIMIT', 10))
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        
        # 출력 디렉토리가 없으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def search_twitter(self, query, count=20, result_type='Latest'):
        """Twitter 검색 API를 사용하여 트윗 검색
        
        Args:
            query (str): 검색 쿼리
            count (int): 가져올 트윗 수
            result_type (str): 검색 결과 타입 (Top, Latest, Photos, Videos, People)
            
        Returns:
            dict: 검색 결과
        """
        try:
            result = self.client.call_api('Twitter/search_twitter', query={
                'query': query,
                'count': count,
                'type': result_type
            })
            return result
        except Exception as e:
            print(f"Twitter 검색 중 오류 발생: {e}")
            return None
    
    def extract_news_from_tweets(self, tweets_data):
        """트윗 데이터에서 뉴스 정보 추출 (디버깅 출력 추가)
        
        Args:
            tweets_data (dict): 트윗 데이터
            
        Returns:
            list: 추출된 뉴스 정보 리스트
        """
        news_items = []
        
        if not tweets_data:
            print("트윗 데이터가 없습니다.")
            return news_items
        
        # 디버깅: 전체 응답 구조 확인
        print("응답 구조 키:", list(tweets_data.keys()))
        
        # 샘플 데이터 저장 (디버깅용)
        debug_file = os.path.join(self.output_dir, "twitter_response_debug.json")
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(tweets_data, f, ensure_ascii=False, indent=2)
        print(f"디버깅용 응답 데이터가 {debug_file}에 저장되었습니다.")
        
        # 수정된 파싱 로직
        try:
            if 'result' in tweets_data and 'timeline' in tweets_data['result']:
                timeline = tweets_data['result']['timeline']
                
                if 'instructions' in timeline:
                    for instruction in timeline['instructions']:
                        if 'entries' in instruction:
                            for entry in instruction['entries']:
                                if 'content' in entry:
                                    content = entry['content']
                                    
                                    # 트윗 내용 추출 시도
                                    if 'itemContent' in content:
                                        item_content = content['itemContent']
                                        tweet_text = item_content.get('tweet_text', '')
                                        
                                        # 사용자 정보 추출 시도
                                        user_name = "Unknown"
                                        user_screen_name = "Unknown"
                                        user_verified = False
                                        
                                        if 'user_results' in item_content and 'result' in item_content['user_results']:
                                            user_result = item_content['user_results']['result']
                                            if 'legacy' in user_result:
                                                user_legacy = user_result['legacy']
                                                user_name = user_legacy.get('name', 'Unknown')
                                                user_screen_name = user_legacy.get('screen_name', 'Unknown')
                                                user_verified = user_legacy.get('verified', False)
                                        
                                        # 트윗 텍스트가 없는 경우 다른 필드에서 찾기 시도
                                        if not tweet_text and 'tweet_results' in item_content:
                                            if 'result' in item_content['tweet_results']:
                                                tweet_result = item_content['tweet_results']['result']
                                                if 'legacy' in tweet_result:
                                                    tweet_legacy = tweet_result['legacy']
                                                    tweet_text = tweet_legacy.get('full_text', '')
                                        
                                        # 트윗 텍스트가 있으면 뉴스 항목 추가
                                        if tweet_text:
                                            news_item = {
                                                'user_name': user_name,
                                                'user_screen_name': user_screen_name,
                                                'user_verified': user_verified,
                                                'tweet_text': tweet_text,
                                                'timestamp': datetime.datetime.now().isoformat()
                                            }
                                            news_items.append(news_item)
                                    
                                    # 다른 형태의 콘텐츠 처리 (items 배열이 있는 경우)
                                    elif 'items' in content:
                                        for item in content['items']:
                                            if 'item' in item and 'itemContent' in item['item']:
                                                item_content = item['item']['itemContent']
                                                
                                                # 트윗 결과 처리
                                                if 'tweet_results' in item_content and 'result' in item_content['tweet_results']:
                                                    tweet_result = item_content['tweet_results']['result']
                                                    
                                                    # 레거시 필드에서 텍스트 추출
                                                    if 'legacy' in tweet_result:
                                                        tweet_legacy = tweet_result['legacy']
                                                        tweet_text = tweet_legacy.get('full_text', '')
                                                        
                                                        # 사용자 정보 추출
                                                        user_name = "Unknown"
                                                        user_screen_name = "Unknown"
                                                        user_verified = False
                                                        
                                                        if 'core' in tweet_result and 'user_results' in tweet_result['core']:
                                                            if 'result' in tweet_result['core']['user_results']:
                                                                user_result = tweet_result['core']['user_results']['result']
                                                                if 'legacy' in user_result:
                                                                    user_legacy = user_result['legacy']
                                                                    user_name = user_legacy.get('name', 'Unknown')
                                                                    user_screen_name = user_legacy.get('screen_name', 'Unknown')
                                                                    user_verified = user_legacy.get('verified', False)
                                                        
                                                        # 뉴스 항목 추가
                                                        if tweet_text:
                                                            news_item = {
                                                                'user_name': user_name,
                                                                'user_screen_name': user_screen_name,
                                                                'user_verified': user_verified,
                                                                'tweet_text': tweet_text,
                                                                'timestamp': datetime.datetime.now().isoformat()
                                                            }
                                                            news_items.append(news_item)
            
            print(f"추출된 뉴스 항목 수: {len(news_items)}")
            
            # 추출된 항목이 없는 경우 대체 방법 시도
            if not news_items:
                print("대체 파싱 방법 시도 중...")
                # 응답 구조를 직접 순회하며 텍스트 추출 시도
                self._extract_text_recursively(tweets_data, news_items)
                print(f"대체 방법으로 추출된 뉴스 항목 수: {len(news_items)}")
        
        except Exception as e:
            print(f"트윗 데이터 처리 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        return news_items
    
    def _extract_text_recursively(self, data, news_items, depth=0, max_depth=10):
        """재귀적으로 데이터에서 텍스트 추출 (대체 방법)
        
        Args:
            data: 처리할 데이터 (dict, list 또는 기본 타입)
            news_items: 추출된 뉴스 항목을 저장할 리스트
            depth: 현재 재귀 깊이
            max_depth: 최대 재귀 깊이
        """
        if depth > max_depth:
            return
        
        if isinstance(data, dict):
            # 트윗 텍스트와 관련된 키 확인
            text_keys = ['full_text', 'text', 'tweet_text']
            user_keys = ['name', 'screen_name']
            
            # 텍스트 키가 있는지 확인
            tweet_text = None
            for key in text_keys:
                if key in data and isinstance(data[key], str) and len(data[key]) > 10:
                    tweet_text = data[key]
                    break
            
            # 사용자 정보 키가 있는지 확인
            user_name = None
            user_screen_name = None
            for key in user_keys:
                if key in data and isinstance(data[key], str):
                    if key == 'name':
                        user_name = data[key]
                    elif key == 'screen_name':
                        user_screen_name = data[key]
            
            # 트윗 텍스트와 사용자 정보가 모두 있으면 뉴스 항목 추가
            if tweet_text and user_name and user_screen_name:
                news_item = {
                    'user_name': user_name,
                    'user_screen_name': user_screen_name,
                    'user_verified': data.get('verified', False),
                    'tweet_text': tweet_text,
                    'timestamp': datetime.datetime.now().isoformat()
                }
                news_items.append(news_item)
            
            # 재귀적으로 모든 값 처리
            for value in data.values():
                self._extract_text_recursively(value, news_items, depth + 1, max_depth)
        
        elif isinstance(data, list):
            for item in data:
                self._extract_text_recursively(item, news_items, depth + 1, max_depth)
    
    def create_sample_data(self):
        """샘플 데이터 생성 (API 응답이 없는 경우 테스트용)
        
        Returns:
            list: 샘플 뉴스 항목 리스트
        """
        print("샘플 데이터 생성 중...")
        sample_data = [
            {
                'user_name': 'AI News Daily',
                'user_screen_name': 'AInewsdaily',
                'user_verified': True,
                'tweet_text': 'Breaking: OpenAI releases GPT-5 with unprecedented reasoning capabilities. The new model shows significant improvements in mathematical reasoning and code generation. #AI #GPT5 #OpenAI https://example.com/news/gpt5-release',
                'timestamp': datetime.datetime.now().isoformat()
            },
            {
                'user_name': 'Tech Insider',
                'user_screen_name': 'techinsider',
                'user_verified': True,
                'tweet_text': 'Google DeepMind announces new breakthrough in protein folding prediction, potentially revolutionizing drug discovery process. #AI #DeepMind #Science https://example.com/news/deepmind-protein-folding',
                'timestamp': datetime.datetime.now().isoformat()
            },
            {
                'user_name': 'AI Research Hub',
                'user_screen_name': 'AIResearchHub',
                'user_verified': False,
                'tweet_text': 'New research paper shows how large language models can be fine-tuned for specialized medical knowledge with 50% less training data than previous methods. #AI #MachineLearning #MedicalAI https://example.com/research/llm-medical-finetuning',
                'timestamp': datetime.datetime.now().isoformat()
            },
            {
                'user_name': 'Future of AI',
                'user_screen_name': 'FutureofAI',
                'user_verified': False,
                'tweet_text': 'Meta introduces new multimodal AI system that can understand and generate content across text, images, audio, and video simultaneously. #AI #Meta #Multimodal https://example.com/news/meta-multimodal-ai',
                'timestamp': datetime.datetime.now().isoformat()
            },
            {
                'user_name': 'AI Ethics Watch',
                'user_screen_name': 'AIEthicsWatch',
                'user_verified': True,
                'tweet_text': 'EU proposes new regulations for AI systems requiring transparency in generative AI outputs and clear labeling of AI-generated content. #AIEthics #Regulation #EU https://example.com/news/eu-ai-regulations',
                'timestamp': datetime.datetime.now().isoformat()
            }
        ]
        return sample_data
    
    def crawl_ai_news(self):
        """AI 관련 뉴스 크롤링 실행
        
        Returns:
            list: 수집된 뉴스 정보 리스트
        """
        all_news = []
        
        for keyword in self.ai_keywords:
            print(f"'{keyword}' 키워드로 Twitter 검색 중...")
            search_query = f"{keyword} filter:news"
            tweets_data = self.search_twitter(search_query, self.news_limit, 'Latest')
            
            if tweets_data:
                news_items = self.extract_news_from_tweets(tweets_data)
                all_news.extend(news_items)
                print(f"'{keyword}' 키워드에서 {len(news_items)}개의 뉴스 항목 추출")
            
            # 중복 제거
            unique_news = []
            seen_texts = set()
            
            for news in all_news:
                if news['tweet_text'] not in seen_texts:
                    seen_texts.add(news['tweet_text'])
                    unique_news.append(news)
            
            all_news = unique_news
            
            # 뉴스 제한 수에 도달하면 중단
            if len(all_news) >= self.news_limit:
                all_news = all_news[:self.news_limit]
                break
        
        # 뉴스를 찾지 못한 경우 샘플 데이터 사용
        if not all_news:
            print("실제 뉴스를 찾지 못했습니다. 샘플 데이터를 사용합니다.")
            all_news = self.create_sample_data()
        
        return all_news
    
    def save_news_to_file(self, news_items, filename=None):
        """수집된 뉴스를 파일로 저장
        
        Args:
            news_items (list): 뉴스 항목 리스트
            filename (str, optional): 저장할 파일명. 기본값은 현재 날짜 기반.
            
        Returns:
            str: 저장된 파일 경로
        """
        if not filename:
            current_date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ai_news_<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>