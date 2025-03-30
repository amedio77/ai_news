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

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GPTProcessor:
    """GPT를 사용하여 뉴스 컨텐츠를 생성하는 클래스"""
    
    def __init__(self):
        """GPT 프로세서 초기화"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI()
        self.model = "gpt-3.5-turbo"
        
        # 프롬프트 설정 로드
        self.prompts = self._load_prompts()
        
        # 메타데이터 설정
        self.metadata = self.prompts.get('metadata', {})
        self.temperature_settings = self.metadata.get('temperature_settings', {})
        self.max_tokens = self.metadata.get('max_tokens', {})
        
        # 톤 가이드라인 로드
        self.tone_settings = self._load_tone_guidelines()
    
    def _load_prompts(self) -> Dict[str, Any]:
        """프롬프트 설정 로드"""
        try:
            with open('config/prompts.json', 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            logging.info("Loaded prompts configuration from config/prompts.json")
            
            # 톤 가이드라인 로드
            tone_guidelines = self._load_tone_guidelines()
            if tone_guidelines:
                # 시스템 프롬프트에 톤 가이드라인 추가
                for category in prompts:
                    if isinstance(prompts[category], dict) and 'system' in prompts[category]:
                        prompts[category]['system'] = prompts[category]['system'].replace(
                            '{tone_guidelines}', tone_guidelines.get('SYSTEM_PROMPT', '')
                        )
            
            return prompts
            
        except Exception as e:
            logging.error(f"Error loading prompts: {e}")
            return {}
    
    def get_system_prompt(self, prompt_type: str) -> str:
        """시스템 프롬프트 가져오기"""
        return self.prompts.get(prompt_type, {}).get('system', '')
    
    def get_prompt(self, prompt_type: str, prompt_name: str) -> Dict[str, str]:
        """특정 프롬프트 가져오기"""
        return self.prompts.get(prompt_type, {}).get(prompt_name, {})
    
    def get_temperature(self, task_type: str) -> float:
        """작업 유형에 따른 temperature 값 가져오기"""
        return self.temperature_settings.get(task_type, 0.7)
    
    def get_max_tokens(self, task_type: str) -> int:
        """작업 유형에 따른 최대 토큰 수 가져오기"""
        return self.max_tokens.get(task_type, 500)
    
    def format_prompt(self, prompt_type: str, prompt_name: str, **kwargs) -> Dict[str, str]:
        """프롬프트 포맷팅"""
        prompt = self.get_prompt(prompt_type, prompt_name)
        if not prompt:
            return {}
        
        try:
            formatted_content = prompt['content'].format(**kwargs)
            return {
                'role': prompt['role'],
                'content': formatted_content
            }
        except KeyError as e:
            logger.error(f"Missing required parameter for prompt formatting: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            return {}
    
    def prepare_messages(self, prompt_type: str, prompt_name: str, **kwargs) -> List[Dict[str, str]]:
        """GPT 메시지 준비"""
        messages = []
        
        # 시스템 프롬프트 추가
        system_prompt = self.get_system_prompt(prompt_type)
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # 사용자 프롬프트 추가
        user_prompt = self.format_prompt(prompt_type, prompt_name, **kwargs)
        if user_prompt:
            messages.append(user_prompt)
        
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
            'system_prompt': self.prompts.get('research_summary', {}).get('system', ''),
            'user_prompt': self.prompts.get('research_summary', {}).get('paper_summary', {}).get('content', '').format(paper_content=paper_content)
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
            'system_prompt': self.prompts.get('news_summary', {}).get('system', ''),
            'user_prompt': self.prompts.get('news_summary', {}).get('article_summary', {}).get('content', '').format(article_content=article_content)
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
            'system_prompt': self.prompts.get('social_media', {}).get('system', ''),
            'user_prompt': self.prompts.get('social_media', {}).get('content', '').format(article_content=content)
        }

    def _call_gpt_api(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Call OpenAI GPT API with messages."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Log token usage
            if hasattr(response, 'usage'):
                logging.info(f"Token usage - Prompt: {response.usage.prompt_tokens}, "
                            f"Completion: {response.usage.completion_tokens}, "
                            f"Total: {response.usage.total_tokens}")
            
            # Extract content from response
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content
            
            return None
            
        except Exception as e:
            logging.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")
            return None
    
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

    def _analyze_chunk_trends(self, news_data):
        """Analyze trends in a chunk of news data."""
        try:
            # Format news data for analysis
            formatted_entries = []
            for news in news_data:
                source = news.get('user_name', 'Unknown')
                content = news.get('tweet_text', '')
                formatted_entries.append(
                    "Source: {}\nContent: {}".format(source, content)
                )
            chunk_data = "\n\n".join(formatted_entries)
            
            # Prepare prompt for trend analysis
            prompt = self.prompts['news_analysis']['trend_analysis']
            prompt['content'] = prompt['content'].format(news_data=chunk_data)
            
            # Call GPT API for trend analysis
            response = self._call_gpt_api([
                {"role": "system", "content": self.prompts['news_analysis']['system']},
                prompt
            ])
            
            if not response:
                logging.warning("No response from GPT API in _analyze_chunk_trends")
                return ""
            
            return response.strip()
            
        except Exception as e:
            logging.error(f"Error in _analyze_chunk_trends: {str(e)}")
            return ""

    def _combine_trend_analyses(self, trend_analyses: List[str]) -> Dict[str, str]:
        """여러 트렌드 분석을 하나로 통합"""
        combined_trends = "\n\n".join([f"Analysis {i+1}:\n{analysis}" 
                                      for i, analysis in enumerate(trend_analyses)])
        
        messages = self.prepare_messages('news_analysis', 'technical_analysis',
                                       trend_analysis=combined_trends)
        
        response = self._call_gpt_api(messages)
        tech_analysis = response if response else ""
        
        return {
            'trend_analysis': combined_trends,
            'tech_analysis': tech_analysis
        }

    def save_blog_post(self, content: str, meta_description: str) -> str:
        """Save the generated blog post as a markdown file.
        
        Args:
            content (str): Blog post content
            meta_description (str): Meta description
            
        Returns:
            str: Path to the saved file
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
            
            # 메타 설명을 YAML 프론트매터로 추가
            front_matter = "---\n"
            front_matter += "title: {}\n".format(content.split('\n')[0].strip('# '))
            front_matter += "date: {}\n".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            front_matter += "description: {}\n".format(meta_description)
            front_matter += "categories:\n"
            front_matter += "  - AI\n"
            front_matter += "  - 기술\n"
            front_matter += "  - 뉴스\n"
            front_matter += "tags:\n"
            front_matter += "  - 인공지능\n"
            front_matter += "  - 기술동향\n"
            front_matter += "  - 자동화\n"
            front_matter += "---\n\n"
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(front_matter + content)
                
            logging.info(f"블로그가 {filepath}에 저장되었습니다.")
            return filepath
            
        except Exception as e:
            logging.error(f"블로그 저장 중 오류 발생: {str(e)}")
            raise

    def generate_blog_post(self, news_file: str) -> Tuple[str, str]:
        """Generate a blog post from news data."""
        try:
            # Load and preprocess news data
            with open(news_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            # Split data into smaller chunks
            chunks = self._chunk_data(news_data)
            
            # Analyze trends in chunks
            trend_analyses = []
            for chunk in chunks:
                analysis = self._analyze_chunk_trends(chunk)
                if analysis:
                    trend_analyses.append(analysis)
            
            if not trend_analyses:
                raise ValueError("Failed to generate any trend analyses")
            
            # Combine analyses into a single string
            combined_analysis = "\n\n".join(trend_analyses)
            
            # Generate blog post parts
            intro_prompt = self.prompts['content_generation']['news_blog_post_intro']
            intro_prompt['content'] = intro_prompt['content'].format(trend_analysis=combined_analysis[:2000])
            
            intro_response = self._call_gpt_api([
                {"role": "system", "content": self.prompts['content_generation']['system']},
                intro_prompt
            ])
            
            if not intro_response:
                raise ValueError("Failed to generate blog post introduction")
            
            trends_prompt = self.prompts['content_generation']['news_blog_post_trends']
            trends_prompt['content'] = trends_prompt['content'].format(trend_analysis=combined_analysis[2000:4000])
            
            trends_response = self._call_gpt_api([
                {"role": "system", "content": self.prompts['content_generation']['system']},
                trends_prompt
            ])
            
            if not trends_response:
                raise ValueError("Failed to generate blog post trends section")
            
            conclusion_prompt = self.prompts['content_generation']['news_blog_post_conclusion']
            conclusion_prompt['content'] = conclusion_prompt['content'].format(trend_analysis=combined_analysis[4000:])
            
            conclusion_response = self._call_gpt_api([
                {"role": "system", "content": self.prompts['content_generation']['system']},
                conclusion_prompt
            ])
            
            if not conclusion_response:
                raise ValueError("Failed to generate blog post conclusion")
            
            # Combine all parts
            content = f"{intro_response}\n\n{trends_response}\n\n{conclusion_response}"
            
            # Generate meta description
            meta_description = self._generate_meta_description(content[:1000])
            
            # Save blog post
            filepath = self.save_blog_post(content.strip(), meta_description.strip())
            logging.info(f"블로그가 {filepath}에 저장되었습니다.")
            
            return content.strip(), meta_description.strip()
        
        except Exception as e:
            logging.error(f"Error in generate_blog_post: {str(e)}")
            raise

    def optimize_blog_post(self, content: str, keywords: List[str], language: str = 'ko') -> Dict[str, str]:
        """기존 블로그 포스트 SEO 최적화"""
        prompt = self.prepare_prompt('blog_content', 'optimization', language)
        
        optimization_prompt = {
            'role': 'user',
            'content': f"""다음 블로그 포스트를 SEO 관점에서 최적화해주세요.
            
            키워드: {', '.join(keywords)}
            
            원본 콘텐츠:
            {content}
            
            최적화 요구사항:
            1. 키워드를 자연스럽게 배치 (밀도 1-2%)
            2. 제목과 메타 설명 최적화
            3. 헤딩 태그 구조화
            4. 내부/외부 링크 추천
            5. 이미지 최적화 제안"""
        }
        
        messages = [
            {'role': 'system', 'content': prompt.get('system', '')},
            optimization_prompt
        ]
        
        # TODO: GPT API 호출 구현
        optimized_content = "여기에 최적화된 콘텐츠가 들어갈 예정입니다."
        
        return {
            'optimized_content': optimized_content,
            'system_prompt': prompt.get('system', ''),
            'optimization_prompt': optimization_prompt.get('content', '')
        }

    def _load_tone_guidelines(self) -> Dict[str, Any]:
        """톤 가이드라인 설정 로드"""
        try:
            tone_file = os.path.join('config', 'tone_guidelines.txt')
            if not os.path.exists(tone_file):
                logger.warning(f"Tone guidelines file not found: {tone_file}")
                return {}
                
            settings = {
                'SYSTEM_PROMPT': '',
                'RESPONSE_STYLE': {},
                'ACCURACY_GUIDELINES': '',
                'EMPATHY_RULES': '',
                'EXAMPLE_RESPONSES': {}
            }
            
            current_section = None
            current_content = []
            
            with open(tone_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if line.startswith('SYSTEM_PROMPT'):
                    current_section = 'SYSTEM_PROMPT'
                    continue
                elif line.startswith('RESPONSE_STYLE'):
                    current_section = 'RESPONSE_STYLE'
                    continue
                elif line.startswith('ACCURACY_GUIDELINES'):
                    current_section = 'ACCURACY_GUIDELINES'
                    continue
                elif line.startswith('EMPATHY_RULES'):
                    current_section = 'EMPATHY_RULES'
                    continue
                elif line.startswith('EXAMPLE_RESPONSES'):
                    current_section = 'EXAMPLE_RESPONSES'
                    continue
                
                if current_section == 'SYSTEM_PROMPT':
                    if line.startswith('"""'):
                        if settings['SYSTEM_PROMPT']:
                            current_section = None
                        continue
                    settings['SYSTEM_PROMPT'] += line + '\n'
                    
                elif current_section == 'RESPONSE_STYLE':
                    if line.startswith('{'):
                        try:
                            settings['RESPONSE_STYLE'] = eval(line + next(l for l in lines if '}' in l))
                        except:
                            logger.error("Failed to parse RESPONSE_STYLE")
                        current_section = None
                        
                elif current_section == 'ACCURACY_GUIDELINES':
                    if line.startswith('"""'):
                        if settings['ACCURACY_GUIDELINES']:
                            current_section = None
                        continue
                    settings['ACCURACY_GUIDELINES'] += line + '\n'
                    
                elif current_section == 'EMPATHY_RULES':
                    if line.startswith('"""'):
                        if settings['EMPATHY_RULES']:
                            current_section = None
                        continue
                    settings['EMPATHY_RULES'] += line + '\n'
                    
                elif current_section == 'EXAMPLE_RESPONSES':
                    if line.startswith('{'):
                        try:
                            settings['EXAMPLE_RESPONSES'] = eval(line + ''.join(l for l in lines if '}' in l))
                        except:
                            logger.error("Failed to parse EXAMPLE_RESPONSES")
                        current_section = None
            
            logger.info("Successfully loaded tone guidelines")
            return settings
            
        except Exception as e:
            logger.error(f"Error loading tone guidelines: {e}")
            return {}
    
    def _get_response_template(self, response_type: str = '간단한_질문') -> Dict[str, str]:
        """응답 템플릿 가져오기"""
        return self.tone_settings.get('EXAMPLE_RESPONSES', {}).get(response_type, {})
        
    def _format_response(self, content: str, response_type: str = '간단한_질문') -> str:
        """응답 포맷팅"""
        style = self.tone_settings.get('RESPONSE_STYLE', {})
        template = self._get_response_template(response_type)
        
        # 기본 인사말과 맺음말 적용
        greeting = style.get('인사말', '안녕하세요!')
        closing = style.get('맺음말', '더 궁금한 점 있으시면 말씀해주세요.')
        
        formatted_content = f"{greeting}\n\n{content}\n\n{closing}"
        return formatted_content
        
    def prepare_prompt(self, task_type: str, content_type: str, language: str = 'en') -> Dict[str, Any]:
        """프롬프트 준비"""
        prompt = self.prompts.get(task_type, {}).copy()
        
        # 시스템 프롬프트에 톤 가이드라인 추가
        system_prompt = prompt.get('system', '')
        system_prompt = self.tone_settings.get('SYSTEM_PROMPT', '') + '\n\n' + system_prompt
        
        # 정확성 가이드라인 추가
        accuracy = self.tone_settings.get('ACCURACY_GUIDELINES', '')
        if accuracy:
            system_prompt += '\n\n' + accuracy
            
        # 공감 규칙 추가
        empathy = self.tone_settings.get('EMPATHY_RULES', '')
        if empathy:
            system_prompt += '\n\n' + empathy
            
        prompt['system'] = system_prompt
        return prompt 

    def _generate_meta_description(self, content):
        """Generate a concise meta description for the blog post."""
        prompt = self.prompts['content_generation']['meta_description']
        prompt['content'] = prompt['content'].format(
            post_content=content[:1000]  # Only use first 1000 characters for meta description
        )
        
        response = self._call_gpt_api([
            {"role": "system", "content": "당신은 전문 SEO 작가입니다. 정확히 130-140자 길이의 간결하면서도 매력적인 메타 설명을 작성해주세요. 주요 키워드를 포함하고, 독자의 관심을 끌 수 있는 핵심 가치를 반드시 언급해주세요."},
            prompt
        ])
        
        if not response:
            return ""
        
        # 메타 설명 길이 확인 및 조정
        meta = response.strip()
        if len(meta) < 130:
            # 너무 짧은 경우, 내용을 보강하여 다시 생성
            enhanced_prompt = {
                "role": "user",
                "content": f"""다음 메타 설명을 130-140자 길이로 보강해주세요. 핵심 내용은 유지하면서, 
                추가적인 가치 제안이나 구체적인 이점을 포함해주세요:
                
                {meta}"""
            }
            
            enhanced_response = self._call_gpt_api([
                {"role": "system", "content": "당신은 전문 SEO 작가입니다. 주어진 메타 설명을 보강하여 130-140자 길이의 매력적인 설명을 작성해주세요."},
                enhanced_prompt
            ])
            
            if enhanced_response:
                meta = enhanced_response.strip()
        
        if len(meta) > 140:
            # 너무 긴 경우, 140자로 자르되 마지막 문장이 잘리지 않도록 조정
            sentences = meta.split('.')
            truncated = ''
            for sentence in sentences:
                if len(truncated + sentence + '.') <= 140:
                    truncated += sentence + '.'
                else:
                    break
            meta = truncated.strip()
        
        return meta 