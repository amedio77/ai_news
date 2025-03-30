#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPT를 사용한 뉴스 컨텐츠 생성 프로세서
"""

import os
import json
import logging
import re
import datetime
from openai import OpenAI
from typing import Dict, List, Optional, Any, Union, Tuple
from ..core.utils import format_filename, save_metadata
from ..core.logger import GPTLogger
from pathlib import Path
import glob
from dateutil.parser import parse

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GPTProcessor:
    """GPT를 사용하여 뉴스 컨텐츠를 생성하는 클래스"""
    
    def __init__(self, api_key: str):
        """GPTProcessor 초기화

        Args:
            api_key (str): OpenAI API 키
        """
        # 로거 초기화
        self.logger = logging.getLogger(__name__)
        self.gpt_logger = GPTLogger()

        # API 클라이언트 초기화
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"

        # 설정 초기화
        self.temperature_settings = {
            'analysis': 0.4,
            'blog': 0.7
        }
        self.max_tokens = {
            'analysis': 1000,
            'blog_post': 4000,
            'meta_description': 200
        }

        # 프롬프트 로드
        self.prompts_dir = os.path.join('src', 'prompts')
        self.md_prompts = self._load_markdown_prompts()
        self.config_prompts = self._load_config_prompts()
        self.tone_settings = self._load_tone_guidelines()

        # 메타데이터 설정
        self.metadata = self.config_prompts.get('metadata', {})
        self.temperature_settings = self.metadata.get('default_settings', {}).get('temperature', {})
        self.max_tokens = self.metadata.get('default_settings', {}).get('max_tokens', {})
    
    def _load_markdown_prompts(self) -> Dict[str, Dict[str, Any]]:
        """마크다운 프롬프트 파일들을 로드합니다.

        Returns:
            Dict[str, Dict[str, Any]]: 로드된 프롬프트 데이터
        """
        prompts = {}
        try:
            # 프롬프트 디렉토리 내의 모든 .md 파일 검색
            prompt_files = glob.glob(os.path.join(self.prompts_dir, "*.md"))
            
            for file_path in prompt_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # JSON 블록 추출
                    json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
                    if not json_blocks:
                        self.logger.warning(f"No JSON blocks found in {os.path.basename(file_path)}")
                        continue

                    # 모든 JSON 블록을 하나의 딕셔너리로 통합
                    prompt_data = {}
                    for block in json_blocks:
                        try:
                            self.logger.debug(f"Parsing JSON block in {os.path.basename(file_path)}:\n{block}")
                            block_data = json.loads(block)
                            prompt_data.update(block_data)
                        except json.JSONDecodeError as e:
                            self.logger.error(f"Error parsing JSON block in {os.path.basename(file_path)}: {str(e)}")
                            continue

                    if prompt_data:  # 파싱된 데이터가 있는 경우에만 저장
                        file_name = os.path.basename(file_path)
                        name_without_ext = os.path.splitext(file_name)[0]
                        prompts[name_without_ext] = prompt_data
                        self.logger.info(f"Loaded prompt from {file_name} with data: {prompt_data}")

                except Exception as e:
                    self.logger.error(f"Error reading {os.path.basename(file_path)}: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in _load_markdown_prompts: {str(e)}")

        return prompts

    def _load_config_prompts(self) -> Dict[str, Any]:
        """config/prompts.json 파일을 로드합니다."""
        try:
            with open('config/prompts.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config prompts: {e}")
            return {}

    def _load_tone_guidelines(self) -> Dict[str, str]:
        """톤 가이드라인을 로드합니다."""
        try:
            with open('config/tone_guidelines.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                return {'SYSTEM_PROMPT': content}
        except Exception as e:
            self.logger.error(f"Error loading tone guidelines: {e}")
            return {}

    def get_prompt(self, prompt_type: str, prompt_name: str = None) -> Dict[str, Any]:
        """프롬프트를 가져옵니다.

        Args:
            prompt_type (str): 프롬프트 타입 (예: 'news_analysis', 'blog_content')
            prompt_name (str, optional): 프롬프트 이름. Defaults to None.

        Returns:
            Dict[str, Any]: 프롬프트 데이터
        """
        try:
            # 프롬프트 데이터 가져오기
            prompt_data = self.md_prompts.get(prompt_type, {})
            if not prompt_data:
                self.logger.warning(f"No prompt file found for {prompt_type}")
                return {}
            
            if not prompt_name:
                return prompt_data.get("system", {})
            
            # prompt_name이 있는 경우 해당 프롬프트 찾기
            if prompt_name in prompt_data:
                return prompt_data[prompt_name]
            
            # 중첩된 구조에서 찾기
            for key, value in prompt_data.items():
                if isinstance(value, dict):
                    if prompt_name in value:
                        return value[prompt_name]
                    # 한 단계 더 깊이 탐색
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, dict) and prompt_name in subvalue:
                            return subvalue[prompt_name]
            
            return {}

        except Exception as e:
            self.logger.error(f"Error in get_prompt: {str(e)}")
            return {}

    def prepare_messages(self, prompt_type: str, prompt_name: str = None, **kwargs) -> List[Dict[str, str]]:
        """GPT API 호출을 위한 메시지를 준비합니다.

        Args:
            prompt_type (str): 프롬프트 타입 (예: 'news_analysis', 'blog_content')
            prompt_name (str, optional): 프롬프트 이름. Defaults to None.
            **kwargs: 추가 인자 (예: news_data)

        Returns:
            List[Dict[str, str]]: 준비된 메시지 리스트
        """
        messages = []
        
        # 시스템 프롬프트 추가
        system_prompt = self.get_prompt(prompt_type, "system")
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 사용자 프롬프트 준비
        if prompt_name:
            user_prompt = self.get_prompt(prompt_type, prompt_name)
            if user_prompt:
                # news_data가 있는 경우 처리
                if "news_data" in kwargs:
                    news_data = kwargs["news_data"]
                    formatted_news = "\n\n".join([
                        f"제목: {item.get('title', '')}\n"
                        f"내용: {item.get('content', '')}\n"
                        f"출처: {item.get('source', '')}\n"
                        f"날짜: {item.get('created_at', '')}"
                        for item in news_data
                    ])
                    user_prompt = user_prompt.format(news_data=formatted_news)
                
                # blog_content가 있는 경우 처리
                elif "blog_content" in kwargs:
                    user_prompt = user_prompt.format(blog_content=kwargs["blog_content"])
                
                # news_content가 있는 경우 처리
                elif "news_content" in kwargs:
                    user_prompt = user_prompt.format(news_content=kwargs["news_content"])
                
                # trend_analysis가 있는 경우 처리
                elif "trend_analysis" in kwargs:
                    user_prompt = user_prompt.format(trend_analysis=kwargs["trend_analysis"])

                messages.append({"role": "user", "content": user_prompt})

        return messages
    
    def process_article(self, article_content: str, process_type: str = 'news_summary') -> Dict[str, Any]:
        """기사 처리"""
        results = {}
        
        if process_type == 'news_summary':
            # 기사 요약
            messages = self.prepare_messages('news_summary', 'article_summary', 
                                          article_content=article_content)
            if messages:
                # TODO: GPT API 호출 구현
                summary = "GPT API 호출 결과가 여기에 들어갈 예정"
                results['summary'] = summary
                
                # 트윗 생성
                tweet_messages = self.prepare_messages('news_summary', 'tweet_generation',
                                                    summary=summary)
                if tweet_messages:
                    # TODO: GPT API 호출 구현
                    tweet = "트윗 생성 결과가 여기에 들어갈 예정"
                    results['tweet'] = tweet
                
                # 한국어 번역
                translation_messages = self.prepare_messages('news_summary', 'korean_translation',
                                                          english_summary=summary)
                if translation_messages:
                    # TODO: GPT API 호출 구현
                    translation = "한국어 번역 결과가 여기에 들어갈 예정"
                    results['translation'] = translation
        
        elif process_type == 'news_analysis':
            # 기술 분석
            tech_messages = self.prepare_messages('news_analysis', 'technical_analysis',
                                               article_content=article_content)
            if tech_messages:
                # TODO: GPT API 호출 구현
                results['technical_analysis'] = "기술 분석 결과"
            
            # 트렌드 분석
            trend_messages = self.prepare_messages('news_analysis', 'trend_analysis',
                                                article_content=article_content)
            if trend_messages:
                # TODO: GPT API 호출 구현
                results['trend_analysis'] = "트렌드 분석 결과"
        
        elif process_type == 'content_generation':
            # 블로그 포스트 생성
            blog_messages = self.prepare_messages('content_generation', 'blog_post',
                                               article_content=article_content)
            if blog_messages:
                # TODO: GPT API 호출 구현
                results['blog_post'] = "생성된 블로그 포스트"
            
            # 소셜 미디어 포스트 생성
            social_messages = self.prepare_messages('content_generation', 'social_media',
                                                 article_content=article_content)
            if social_messages:
                # TODO: GPT API 호출 구현
                results['social_media_posts'] = "생성된 소셜 미디어 포스트"
        
        return results
    
    def process_research_paper(self, paper_content: str) -> Dict[str, str]:
        """연구 논문 처리"""
        messages = self.prepare_messages('research_summary', 'paper_summary',
                                      paper_content=paper_content)
        if not messages:
            return {}
            
        # TODO: GPT API 호출 구현
        summary = "연구 논문 요약이 여기에 들어갈 예정"
        
        return {
            'summary': summary,
            'system_prompt': self.tone_settings.get('SYSTEM_PROMPT', ''),
            'user_prompt': self.tone_settings.get('paper_summary', {}).get('content', '').format(paper_content=paper_content)
        }
    
    def process_news_article(self, article_content: str) -> Dict[str, str]:
        """뉴스 기사 처리"""
        messages = self.prepare_messages('news_summary', 'article_summary',
                                      article_content=article_content)
        if not messages:
            return {}
            
        # TODO: GPT API 호출 구현
        summary = "뉴스 기사 요약이 여기에 들어갈 예정"
        
        return {
            'summary': summary,
            'system_prompt': self.tone_settings.get('SYSTEM_PROMPT', ''),
            'user_prompt': self.tone_settings.get('article_summary', {}).get('content', '').format(article_content=article_content)
        }

    def generate_social_content(self, content: str) -> Dict[str, str]:
        """소셜 미디어 콘텐츠 생성"""
        messages = self.prepare_messages('social_media', 'content_generation',
                                      article_content=content)
        if not messages:
            return {}
            
        # TODO: GPT API 호출 구현
        social_content = "소셜 미디어 콘텐츠가 여기에 들어갈 예정"
        
        return {
            'content': social_content,
            'system_prompt': self.tone_settings.get('SYSTEM_PROMPT', ''),
            'user_prompt': self.tone_settings.get('content', '').format(article_content=content)
        }

    def _call_gpt(self, messages: List[Dict[str, str]], temperature: float = 0.4, max_tokens: int = 1000) -> str:
        """GPT API를 호출합니다.

        Args:
            messages (List[Dict[str, str]]): 메시지 리스트
            temperature (float, optional): 온도 설정. Defaults to 0.4.
            max_tokens (int, optional): 최대 토큰 수. Defaults to 1000.

        Returns:
            str: GPT API 응답 내용
        """
        try:
            if not messages:
                self.logger.error("Empty messages array")
                return ""

            # GPT API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            if not response or not response.choices or not response.choices[0].message.content:
                self.logger.error("No content in GPT response")
                return ""

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Error in _call_gpt: {str(e)}")
            return ""
    
    def _preprocess_news_data(self, news_data: List[Dict]) -> List[Dict]:
        """뉴스 데이터 전처리
        - HTML 태그 제거
        - 중복 내용 제거
        - URL 제거
        """
        processed_data = []
        seen_content = set()
        
        for news in news_data:
            # HTML 태그 제거
            text = re.sub(r'<[^>]+>', '', news['tweet_text'])
            text = re.sub(r'\s+', ' ', text).strip()
            
            # URL 제거
            text = re.sub(r'http\S+', '', text).strip()
            
            # 중복 체크 (첫 100자로 판단)
            content_key = text[:100]
            if content_key in seen_content:
                continue
            seen_content.add(content_key)
            
            processed_data.append({
                'source': news['user_name'],
                'content': text,
                'created_at': news['created_at']
            })
        
        return processed_data

    def _chunk_data(self, news_data: List[Dict], chunk_size: int = 5) -> List[List[Dict]]:
        """Split news data into smaller chunks for processing."""
        return [news_data[i:i + chunk_size] for i in range(0, len(news_data), chunk_size)]

    def _format_source_citation(self, source_data: Dict[str, Any]) -> str:
        """뉴스 출처 정보를 포맷팅합니다.

        Args:
            source_data (Dict[str, Any]): 출처 데이터

        Returns:
            str: 포맷팅된 출처 정보
        """
        try:
            source_name = source_data.get('name', '출처 미상')
            date_str = source_data.get('date', '')
            url = source_data.get('url', '')
            
            # 날짜 포맷팅
            try:
                if date_str:
                    date_obj = parse(date_str)
                    date_str = date_obj.strftime('%Y년 %m월 %d일')
            except Exception as e:
                logger.warning(f"날짜 파싱 실패: {str(e)}")
                date_str = ''
            
            # 출처 문자열 생성
            citation = f"(출처: {source_name}"
            if date_str:
                citation += f", {date_str}"
            citation += ")"
            
            # URL이 있는 경우 마크다운 링크 형식으로 추가
            if url:
                citation = f"[{citation}]({url})"
            
            return citation
        except Exception as e:
            logger.error(f"출처 포맷팅 중 오류 발생: {str(e)}")
            return "(출처: 확인 불가)"

    def _apply_tone_guidelines(self, content: str, content_type: str = 'blog') -> str:
        """톤 가이드라인 적용
        
        Args:
            content (str): 원본 컨텐츠
            content_type (str): 컨텐츠 유형 (blog, analysis 등)
            
        Returns:
            str: 톤 가이드라인이 적용된 컨텐츠
        """
        try:
            # 응답 스타일 적용
            style = self.tone_settings.get('RESPONSE_STYLE', {})
            if style:
                # 인사말 추가 (블로그 포스트인 경우에만)
                if content_type == 'blog' and style.get('인사말'):
                    content = f"{style['인사말']}\n\n{content}"
                
                # 맺음말 추가 (블로그 포스트인 경우에만)
                if content_type == 'blog' and style.get('맺음말'):
                    content = f"{content}\n\n{style['맺음말']}"
            
            # 정확성 가이드라인 적용
            accuracy = self.tone_settings.get('ACCURACY_GUIDELINES', '')
            if accuracy:
                content = self._apply_accuracy_guidelines(content)
            
            # 공감 규칙 적용
            empathy = self.tone_settings.get('EMPATHY_RULES', '')
            if empathy:
                content = self._apply_empathy_rules(content)
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error applying tone guidelines: {e}")
            return content

    def _apply_accuracy_guidelines(self, content: str) -> str:
        """정확성 가이드라인 적용"""
        try:
            # 기술 용어 검증
            content = self._verify_technical_terms(content)
            
            # 출처 형식 검증
            content = self._verify_source_citations(content)
            
            return content
        except Exception as e:
            logger.error(f"Error applying accuracy guidelines: {e}")
            return content

    def _apply_empathy_rules(self, content: str) -> str:
        """공감 규칙 적용"""
        try:
            # 독자 관점 강화
            content = self._enhance_reader_perspective(content)
            
            # 실용적 인사이트 강화
            content = self._enhance_practical_insights(content)
            
            return content
        except Exception as e:
            logger.error(f"Error applying empathy rules: {e}")
            return content

    def _verify_technical_terms(self, content: str) -> str:
        """기술 용어 검증 및 보완"""
        # 기술 용어 설명 추가
        term_pattern = r'\b(AI|ML|DL|NLP|CV|RL)\b(?![^<]*>)'
        term_explanations = {
            'AI': '인공지능(AI)',
            'ML': '머신러닝(ML)',
            'DL': '딥러닝(DL)',
            'NLP': '자연어처리(NLP)',
            'CV': '컴퓨터 비전(CV)',
            'RL': '강화학습(RL)'
        }
        
        for term, explanation in term_explanations.items():
            content = re.sub(f'\\b{term}\\b(?![^<]*>)', explanation, content)
        
        return content

    def _verify_source_citations(self, content: str) -> str:
        """출처 인용 형식 검증"""
        # 출처 형식 검증
        source_pattern = r'\[출처: ([^,\]]+)(?:, 날짜: (\d{4}-\d{2}-\d{2}))?\]'
        
        def fix_citation(match):
            source = match.group(1)
            date = match.group(2)
            if date:
                return f"[출처: {source}, 날짜: {date}]"
            return f"[출처: {source}]"
        
        content = re.sub(source_pattern, fix_citation, content)
        return content

    def _enhance_reader_perspective(self, content: str) -> str:
        """독자 관점 강화"""
        # 전문 용어 설명 추가
        content = re.sub(r'(?<!\w)(?:이는|이것은|이러한)\s', '이러한 기술 발전은 ', content)
        content = re.sub(r'(?<!\w)향후\s', '향후 우리 산업에서 ', content)
        return content

    def _enhance_practical_insights(self, content: str) -> str:
        """실용적 인사이트 강화"""
        # 실용적 관점 추가
        content = re.sub(r'(?<=\. )이는 (?=\w)', '이는 실제 비즈니스에서 ', content)
        content = re.sub(r'(?<=\. )이를 통해 (?=\w)', '이를 통해 기업들은 ', content)
        return content

    def _analyze_chunk_trends(self, news_chunk: List[Dict[str, Any]]) -> str:
        """뉴스 청크에서 트렌드를 분석합니다.

        Args:
            news_chunk (List[Dict[str, Any]]): 분석할 뉴스 청크

        Returns:
            str: 트렌드 분석 결과
        """
        try:
            # 뉴스 데이터 준비
            news_data = []
            for news in news_chunk:
                news_data.append({
                    "title": news.get("title", ""),
                    "content": news.get("tweet_text", ""),
                    "source": news.get("user_name", ""),
                    "created_at": news.get("created_at", "")
                })

            # 메시지 준비
            messages = self.prepare_messages(
                prompt_type="news_analysis",
                prompt_name="trend_analysis",
                news_data=news_data
            )

            # GPT 호출
            response = self._call_gpt(messages)
            if not response:
                self.logger.error("No content in GPT response")
                return ""

            return response

        except Exception as e:
            self.logger.error(f"Error in _analyze_chunk_trends: {str(e)}")
            return ""

    def _combine_trend_analyses(self, trend_analyses: List[str]) -> Dict[str, str]:
        """여러 트렌드 분석을 하나로 통합"""
        combined_trends = "\n\n".join([f"Analysis {i+1}:\n{analysis}" 
                                      for i, analysis in enumerate(trend_analyses)])
        
        messages = self.prepare_messages('news_analysis', 'technical_analysis',
                                       trend_analysis=combined_trends)
        
        tech_analysis = self._call_gpt(messages)
        
        return {
            'trend_analysis': combined_trends,
            'tech_analysis': tech_analysis if tech_analysis else ""
        }

    def save_blog_post(self, content: str, meta_description: str) -> str:
        """블로그 포스트를 마크다운 파일로 저장합니다.

        Args:
            content (str): 블로그 내용
            meta_description (str): 메타 설명
            
        Returns:
            str: 저장된 파일 경로
        """
        try:
            # 저장할 디렉토리 생성
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output')
            blogs_dir = os.path.join(output_dir, 'blogs')
            os.makedirs(blogs_dir, exist_ok=True)
            
            # 파일명 생성
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ai_blog_{timestamp}.md"
            filepath = os.path.join(blogs_dir, filename)
            
            # 제목 추출 (첫 번째 '#' 헤더)
            title = ''
            for line in content.split('\n'):
                if line.startswith('# '):
                    title = line.strip('# ')
                    break
            if not title:
                title = 'AI 기술 동향 분석'
            
            # YAML 프론트매터 생성
            front_matter = "---\n"
            front_matter += f"title: {title}\n"
            front_matter += f"date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            front_matter += f"description: {meta_description}\n"
            front_matter += "categories:\n"
            front_matter += "  - AI\n"
            front_matter += "  - 기술\n"
            front_matter += "  - 트렌드\n"
            front_matter += "tags:\n"
            front_matter += "  - 인공지능\n"
            front_matter += "  - 기술동향\n"
            front_matter += "  - 산업분석\n"
            front_matter += "---\n\n"
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(front_matter + content)
                f.flush()
                os.fsync(f.fileno())  # 파일이 디스크에 완전히 저장되도록 보장
            
            logger.info(f"블로그가 {filepath}에 저장되었습니다.")
            return filepath
            
        except Exception as e:
            logger.error(f"블로그 저장 중 오류 발생: {str(e)}")
            raise

    def process_news_with_sources(self, news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """뉴스 데이터를 출처와 함께 처리합니다.

        Args:
            news_data (List[Dict[str, Any]]): 원본 뉴스 데이터 리스트

        Returns:
            List[Dict[str, Any]]: 처리된 뉴스 데이터 리스트
        """
        processed_news = []
        for news in news_data:
            processed_item = {
                'title': news.get('cleaned_text', '').split('\n')[0],  # 첫 줄을 제목으로 사용
                'content': news.get('cleaned_text', ''),
                'source': news.get('source', ''),
                'timestamp': news.get('timestamp', ''),
                'urls': news.get('urls', []),
                'user_name': news.get('user_name', '')
            }
            processed_news.append(processed_item)
        
        return processed_news

    def analyze_news_by_category(self, processed_news: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """처리된 뉴스를 카테고리별로 분류하고 분석합니다.

        Args:
            processed_news (List[Dict[str, Any]]): 처리된 뉴스 데이터 리스트

        Returns:
            Dict[str, List[Dict[str, Any]]]: 카테고리별로 분류된 뉴스 분석 결과
        """
        # 카테고리 정의
        categories = {
            'technical_advances': [],  # 기술적 진보
            'business_impact': [],     # 비즈니스 영향
            'ethical_concerns': [],    # 윤리적 문제
            'research_developments': [],# 연구 개발
            'industry_applications': [] # 산업 응용
        }
        
        for news in processed_news:
            # 각 뉴스 항목에 대해 GPT를 사용하여 카테고리 분류
            messages = [
                {"role": "system", "content": "다음 뉴스를 분석하여 가장 적합한 카테고리를 선택하세요: technical_advances, business_impact, ethical_concerns, research_developments, industry_applications"},
                {"role": "user", "content": f"제목: {news['title']}\n내용: {news['content']}\n출처: {news['source']} ({news['user_name']})"}
            ]
            
            response = self._call_gpt(messages, temperature=0.3)
            category = response.strip().lower()
            
            if category in categories:
                categories[category].append(news)
        
        return categories

    def generate_blog_post(self, news_file: str) -> Tuple[str, str]:
        """뉴스 데이터를 기반으로 블로그 포스트를 생성합니다.

        Args:
            news_file (str): 뉴스 데이터 파일 경로

        Returns:
            Tuple[str, str]: 생성된 블로그 포스트 내용과 메타 설명
        """
        try:
            # 뉴스 데이터 처리
            processed_news = self._process_news_data(news_file)
            if not processed_news:
                raise ValueError("No valid news data found")
            
            # 블로그 컨텐츠 생성
            blog_content = self._generate_blog_content(processed_news)
            if not blog_content:
                raise ValueError("Failed to generate blog content")
            
            # 메타 설명 생성
            meta_description = self._generate_meta_description(blog_content)
            
            # 블로그 저장
            self.save_blog_post(blog_content, meta_description)
            
            return blog_content, meta_description
        
        except Exception as e:
            self.logger.error(f"Error in generate_blog_post: {str(e)}")
            raise

    def _process_news_data(self, news_file: str) -> List[Dict[str, Any]]:
        """Process news data from a JSON file."""
        try:
            # Load JSON data from file
            with open(news_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            # Ensure news_data is a list
            if not isinstance(news_data, list):
                news_data = [news_data]
            
            processed_news = []
            for news in news_data:
                try:
                    if not isinstance(news, dict):
                        self.logger.warning(f"Skipping non-dict news item: {news}")
                        continue
                    
                    # Extract tweet text and clean it
                    tweet_text = news.get('tweet_text', '')
                    if not tweet_text:
                        self.logger.warning(f"Skipping news item with empty tweet_text: {news}")
                        continue
                    
                    # Split into lines and remove empty ones
                    lines = [line.strip() for line in tweet_text.split('\n') if line.strip()]
                    if not lines:
                        self.logger.warning(f"Skipping news item with no content after cleaning: {news}")
                        continue
                    
                    # First non-empty line is the title
                    title = lines[0]
                    
                    # Remaining lines are content (excluding URLs)
                    content_lines = []
                    for line in lines[1:]:
                        if not line.startswith('http'):
                            content_lines.append(line)
                    
                    content = '\n'.join(content_lines)
                    if not content:
                        content = title  # Use title as content if no other content available
                    
                    # Create processed item
                    processed_item = {
                        'title': title,
                        'content': content,
                        'source': news.get('user_name', 'Unknown'),
                        'created_at': news.get('created_at', datetime.datetime.now().isoformat())
                    }
                    
                    self.logger.info(f"Successfully processed news item: {processed_item['title']}")
                    processed_news.append(processed_item)
                    
                except Exception as e:
                    self.logger.error(f"Error processing individual news item: {str(e)}")
                    continue
            
            if not processed_news:
                self.logger.warning("No valid news items found in the file")
                return []
            
            return processed_news
            
        except Exception as e:
            self.logger.error(f"Error processing news data file: {str(e)}")
            return []

    def _generate_blog_content(self, news_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """블로그 포스트 생성"""
        try:
            # 뉴스 데이터 정렬 및 선택
            sorted_news = sorted(news_data, key=lambda x: parse(x['created_at']), reverse=True)[:5]
            
            # 뉴스 데이터 포맷팅
            news_content = "\n\n".join([
                f"뉴스 {i+1}:\n"
                f"제목: {news['tweet_text']}\n"
                f"날짜: {news['created_at']}\n"
                f"출처: {news.get('source', 'Unknown')}"
                for i, news in enumerate(sorted_news)
            ])
            
            # 트렌드 분석 생성
            trend_analysis = self._generate_trend_analysis(news_data)
            
            # 블로그 포스트 생성
            blog_content = self._generate_blog_post(news_content, trend_analysis)
            
            # 메타 설명 생성
            meta_description = self._generate_meta_description(blog_content)
            
            return {
                'blog_content': blog_content,
                'meta_description': meta_description
            }
            
        except Exception as e:
            self.logger.error(f"블로그 포스트 생성 중 오류 발생: {str(e)}")
            raise

    def _generate_blog_post(self, news_content: str, trend_analysis: str) -> str:
        """블로그 포스트 생성"""
        try:
            # 도입부 생성
            intro_prompt = self.prompts['blog_intro'].format(news_content=news_content)
            intro_response = self._call_gpt(intro_prompt)
            intro_content = self._extract_json_content(intro_response)
            
            # 본문 생성
            body_prompt = self.prompts['blog_trends'].format(trend_analysis=trend_analysis)
            body_response = self._call_gpt(body_prompt)
            body_content = self._extract_json_content(body_response)
            
            # 결론 생성
            conclusion_prompt = self.prompts['blog_conclusion'].format(blog_content=f"{intro_content}\n\n{body_content}")
            conclusion_response = self._call_gpt(conclusion_prompt)
            conclusion_content = self._extract_json_content(conclusion_response)
            
            # 전체 블로그 포스트 조합
            blog_post = f"""# AI 기술 동향 분석: 최신 뉴스와 트렌드

{intro_content}

{body_content}

{conclusion_content}

## 참고 자료
- 각 뉴스의 출처와 날짜는 본문에 명시되어 있습니다.
- 모든 데이터는 공개된 뉴스 소스를 기반으로 분석되었습니다.
- 트렌드 분석은 현재 시장 동향과 전문가 의견을 종합하여 작성되었습니다.
"""
            
            return blog_post
            
        except Exception as e:
            self.logger.error(f"블로그 포스트 생성 중 오류 발생: {str(e)}")
            raise

    def _generate_trend_analysis(self, news_data: List[Dict[str, Any]]) -> str:
        """트렌드 분석 생성"""
        try:
            # 뉴스 데이터 포맷팅
            formatted_news = "\n\n".join([
                f"뉴스 {i+1}:\n"
                f"제목: {news['tweet_text']}\n"
                f"날짜: {news['created_at']}\n"
                f"출처: {news.get('source', 'Unknown')}"
                for i, news in enumerate(news_data)
            ])
            
            # 트렌드 분석 프롬프트 생성
            trend_prompt = self.prompts['trend_analysis'].format(news_data=formatted_news)
            
            # GPT API 호출
            response = self._call_gpt(trend_prompt)
            
            # JSON 응답 추출
            trend_analysis = self._extract_json_content(response)
            
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"트렌드 분석 생성 중 오류 발생: {str(e)}")
            raise

    def _generate_meta_description(self, blog_content):
        """Generate meta description for the blog post."""
        return "최신 AI 기술 동향과 산업 영향을 분석한 블로그 포스트입니다. 생성형 AI의 발전, 산업별 활용 사례, 그리고 미래 전망을 다룹니다." 