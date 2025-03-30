# AI News Generator Project Structure

## Overview
AI 뉴스 생성 및 관리를 위한 프로젝트입니다. RSS 피드에서 뉴스를 수집하고, GPT를 활용하여 컨텐츠를 생성하며, WordPress에 자동으로 게시하는 기능을 제공합니다.

## Directory Structure

### Source Code (`src/`)
- **processors/**: 컨텐츠 처리 모듈
  - `gpt_processor.py`: GPT API 통합 및 컨텐츠 생성
  - `__init__.py`: 패키지 초기화
- **crawlers/**: 뉴스 수집 모듈
- **core/**: 핵심 기능 모듈
- **data/**: 데이터 처리 모듈
- **integrations/**: 외부 서비스 통합
- **media/**: 미디어 파일 처리
- **wordpress_integration/**: WordPress 연동
- **gpt_integration/**: GPT API 통합

### Tests (`tests/`)
- `test_blog_content.py`: 블로그 컨텐츠 생성 테스트
- 기타 테스트 모듈

### Configuration (`config/`)
- `prompts.json`: GPT 프롬프트 설정
- `rss_feeds.json`: RSS 피드 설정

### Documentation (`docs/`)
- **prompts/**
  - `tone_guidelines.txt`: 톤/스타일 가이드라인
  - `seo_guidelines.txt`: SEO 최적화 가이드라인

### Data and Output
- **data/**: 원본 데이터 저장
- **output/**: 생성된 컨텐츠 저장
- **logs/**: 로그 파일

### Project Files
- `setup.py`: 프로젝트 설정
- `requirements.txt`: 의존성 관리
- `.env`: 환경 변수 (비공개)
- `.env.example`: 환경 변수 예시

## Key Components

### GPTProcessor
```python
class GPTProcessor:
    def __init__(self, config_dir: str = "config", docs_dir: str = "docs/prompts"):
        # OpenAI API 키 설정
        # 설정 파일 로드
        # 톤 가이드라인 로드
        pass

    def generate_blog_post(self, topic: str, language: str = 'ko') -> Dict[str, str]:
        # 블로그 포스트 생성
        pass

    def _call_gpt_api(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        # GPT API 호출
        pass

    def _load_tone_guidelines(self) -> Dict[str, str]:
        # 톤 가이드라인 로드
        pass
```

### 사용 예시
```python
from processors.gpt_processor import GPTProcessor

# 프로세서 초기화
processor = GPTProcessor()

# 블로그 포스트 생성
topic = "2024 AI 개발자 로드맵"
result = processor.generate_blog_post(topic)

# 결과 출력
print(result['content'])
print(result['meta_description'])
```

## 환경 설정
1. `.env.example`을 `.env`로 복사
2. OpenAI API 키 설정
3. 필요한 패키지 설치: `pip install -r requirements.txt`

## 테스트 실행
```bash
python -m pytest tests/test_blog_content.py -v
``` 