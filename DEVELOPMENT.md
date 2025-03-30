# AI News Crawler 및 Blog Generator 개발 현황

## 1. 현재까지 구현된 기능

### 1.1 크롤링
- [x] Twitter 크롤러 구현
- [x] RSS 크롤러 구현
- [x] 뉴스 데이터 전처리 및 저장

### 1.2 GPT 통합
- [x] OpenAI API 연동
- [x] 프롬프트 설정 관리 (`config/prompts.json`)
- [x] 톤/스타일 가이드라인 관리 (`config/tone_guidelines.txt`)

### 1.3 블로그 생성
- [x] 뉴스 데이터 분석 및 트렌드 추출
- [x] 블로그 포스트 자동 생성
- [x] 메타 설명 생성
- [x] Markdown 형식으로 저장

### 1.4 테스트
- [x] 프롬프트 구조 검증
- [x] 블로그 포스트 생성 테스트
- [x] 메타 설명 길이 검증

## 2. 프로젝트 구조

### 2.1 디렉토리 구조
```
ai_news/
├── config/
│   ├── prompts.json         # GPT 프롬프트 설정
│   └── tone_guidelines.txt  # 톤/스타일 가이드라인
├── data/
│   └── crawled/            # 크롤링된 뉴스 데이터
├── docs/                   # 프로젝트 문서
├── output/
│   └── blogs/             # 생성된 블로그 포스트
├── src/                   # 소스 코드
├── tests/                 # 테스트 코드
├── .env                   # 환경 변수
├── .gitignore            # Git 제외 파일
├── DEVELOPMENT.md        # 개발 문서
├── requirements.txt      # 의존성 목록
└── setup.py             # 패키지 설정
```

### 2.2 프로그램 구조

### 2.3 모듈 구조
```
src/
├── crawlers/
│   ├── __init__.py
│   ├── twitter_crawler.py   # Twitter API를 통한 뉴스 수집
│   ├── rss_crawler.py      # RSS 피드를 통한 뉴스 수집
│   ├── news_processor.py   # 수집된 뉴스 전처리
│   └── main.py            # 크롤러 실행 엔트리포인트
├── processors/
│   ├── __init__.py
│   ├── gpt_processor.py   # GPT 통합 및 블로그 생성
│   └── main.py           # 프로세서 실행 엔트리포인트
└── core/
    ├── __init__.py
    └── utils.py          # 공통 유틸리티 함수
```

### 2.4 주요 클래스 및 메서드

#### TwitterCrawler
- `crawl_tweets()`: 특정 키워드에 대한 트윗 수집
- `process_tweets()`: 수집된 트윗 전처리
- `save_tweets()`: 전처리된 트윗 저장

#### RSSCrawler
- `fetch_feeds()`: RSS 피드에서 뉴스 수집
- `parse_articles()`: 수집된 기사 파싱
- `save_articles()`: 파싱된 기사 저장

#### NewsProcessor
- `preprocess_news()`: 뉴스 데이터 전처리
- `remove_duplicates()`: 중복 뉴스 제거
- `categorize_news()`: 뉴스 카테고리 분류

#### GPTProcessor
- `generate_blog_post()`: 블로그 포스트 생성
- `_analyze_chunk_trends()`: 뉴스 청크 분석
- `_generate_meta_description()`: 메타 설명 생성
- `save_blog_post()`: 블로그 포스트 저장

### 2.5 데이터 흐름
1. 뉴스 수집
   ```mermaid
   graph LR
   A[Twitter API] --> C[TwitterCrawler]
   B[RSS Feeds] --> D[RSSCrawler]
   C --> E[NewsProcessor]
   D --> E
   E --> F[Processed News Data]
   ```

2. 블로그 생성
   ```mermaid
   graph LR
   A[Processed News] --> B[GPTProcessor]
   B --> C[Trend Analysis]
   C --> D[Content Generation]
   D --> E[Meta Description]
   E --> F[Markdown Blog]
   ```

## 3. 최근 변경사항
1. 프롬프트 구조 개선
   - 블로그 포스트 생성을 intro, trends, conclusion 섹션으로 분리
   - 각 섹션별 토큰 제한 관리 개선
2. 메타 설명 생성 로직 개선
   - 길이 제한 (120-160자) 준수
   - SEO 최적화 고려
3. 테스트 코드 업데이트
   - 새로운 프롬프트 구조 반영
   - 블로그 포스트 생성 검증 강화

## 4. 다음 개발 계획
1. 데이터 수집 개선
   - [ ] 추가 뉴스 소스 통합
   - [ ] 크롤링 주기 최적화
   - [ ] 데이터 중복 제거 로직 강화

2. 콘텐츠 생성 개선
   - [ ] 이미지 생성 통합 (DALL-E API)
   - [ ] 다국어 지원
   - [ ] 카테고리별 특화된 프롬프트 개발

3. 배포 및 운영
   - [ ] Docker 컨테이너화
   - [ ] CI/CD 파이프라인 구축
   - [ ] 모니터링 시스템 구축

4. 품질 개선
   - [ ] 코드 커버리지 향상
   - [ ] 성능 최적화
   - [ ] 에러 처리 강화

## 5. 알려진 이슈
1. 토큰 제한으로 인한 긴 뉴스 데이터 처리 문제
   - 현재 해결방안: 청크 단위 처리
   - 개선 필요: 더 효율적인 데이터 분할 방법 연구 중

2. 메타 설명 생성 시 간헐적 길이 초과
   - 현재 해결방안: 반복 생성 및 검증
   - 개선 필요: 더 정확한 길이 제어 방법 개발 중

## 6. 환경 설정
1. 필수 환경 변수 (.env)
   ```
   OPENAI_API_KEY=your_api_key
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   ```

2. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

## 7. 실행 방법
1. 뉴스 크롤링
   ```bash
   python src/crawlers/main.py
   ```

2. 블로그 생성
   ```bash
   python src/processors/main.py
   ```

3. 테스트 실행
   ```bash
   python tests/test_blog_content.py -v
   ```

## 8. 참고 문서
- [OpenAI API 문서](https://platform.openai.com/docs/api-reference)
- [Twitter API 문서](https://developer.twitter.com/en/docs)
- [프로젝트 기술 문서](./docs/CODE_DOCUMENTATION.md)

## 7. 테스트 방법

### 7.1 테스트 구조
```
tests/
├── __init__.py
├── test_blog_content.py     # 블로그 생성 테스트
├── test_crawlers.py         # 크롤러 테스트
└── test_news_processor.py   # 뉴스 처리 테스트
```

### 7.2 단위 테스트
1. 크롤러 테스트
   ```bash
   python -m pytest tests/test_crawlers.py -v
   ```
   - Twitter 크롤러 기능 검증
   - RSS 크롤러 기능 검증
   - 데이터 저장 검증

2. 뉴스 처리 테스트
   ```bash
   python -m pytest tests/test_news_processor.py -v
   ```
   - 전처리 로직 검증
   - 중복 제거 검증
   - 카테고리 분류 검증

3. 블로그 생성 테스트
   ```bash
   python -m pytest tests/test_blog_content.py -v
   ```
   - 프롬프트 구조 검증
   - 콘텐츠 생성 검증
   - 메타 설명 검증

### 7.3 통합 테스트
```bash
python -m pytest tests/ -v
```
- 전체 파이프라인 검증
- 데이터 흐름 검증
- 에러 처리 검증

### 7.4 테스트 커버리지 확인
```bash
python -m pytest tests/ --cov=src --cov-report=html
```
- 테스트 커버리지 리포트 생성
- `htmlcov/index.html`에서 결과 확인

### 7.5 테스트 데이터
- `tests/fixtures/`: 테스트용 샘플 데이터
- `tests/mocks/`: API 모의 응답 데이터
- `tests/conftest.py`: pytest 픽스처 정의 

## 9. 설정 파일 가이드

### 9.1 프롬프트 설정 (prompts.json)
```json
{
    "content_generation": {
        "news_blog_post_intro": {
            "role": "user",
            "content": "..."
        },
        "news_blog_post_trends": {
            "role": "user",
            "content": "..."
        },
        "news_blog_post_conclusion": {
            "role": "user",
            "content": "..."
        }
    },
    "news_analysis": {
        "system": "...",
        "trend_analysis": {
            "role": "user",
            "content": "..."
        }
    }
}
```

### 9.2 톤 가이드라인 (tone_guidelines.txt)
```
SYSTEM_PROMPT
"""
전문적이고 객관적인 톤을 유지하되, 이해하기 쉽게 설명
"""

RESPONSE_STYLE
{
    "tone": "professional",
    "style": "analytical",
    "audience": "tech-savvy readers"
}
```

## 10. 디버깅 가이드

### 10.1 로깅 설정
- 로그 레벨: INFO, DEBUG, ERROR
- 로그 위치: `logs/ai_news.log`
- 로그 포맷: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### 10.2 일반적인 문제 해결
1. OpenAI API 오류
   - 토큰 제한 초과: 청크 크기 조정
   - API 키 오류: .env 파일 확인
   - 요청 실패: 재시도 로직 확인

2. 크롤링 오류
   - Rate Limit: 크롤링 간격 조정
   - 파싱 오류: HTML 구조 변경 확인
   - 네트워크 오류: 타임아웃 설정 확인

3. 데이터 처리 오류
   - 메모리 부족: 배치 처리 적용
   - 인코딩 오류: UTF-8 사용 확인
   - 중복 데이터: 중복 제거 로직 확인

## 11. 개발 가이드라인

### 11.1 코드 스타일
- PEP 8 준수
- Type Hints 사용
- Docstring 필수 작성
- 함수/메서드 길이 제한 (최대 50줄)

### 11.2 Git 워크플로우
1. 브랜치 전략
   - main: 안정 버전
   - develop: 개발 버전
   - feature/*: 기능 개발
   - bugfix/*: 버그 수정
   - release/*: 릴리즈 준비

2. 커밋 메시지 규칙
   ```
   feat: 새로운 기능 추가
   fix: 버그 수정
   docs: 문서 수정
   style: 코드 포맷팅
   refactor: 코드 리팩토링
   test: 테스트 코드
   chore: 기타 변경사항
   ```

### 11.3 코드 리뷰 체크리스트
- [ ] 코드 스타일 준수
- [ ] 테스트 코드 작성
- [ ] 문서화 완료
- [ ] 에러 처리 구현
- [ ] 성능 최적화 검토
- [ ] 보안 고려사항 검토

## 12. 성능 모니터링

### 12.1 모니터링 지표
1. API 응답 시간
   - OpenAI API 호출 시간
   - 크롤링 소요 시간
   - 데이터 처리 시간

2. 리소스 사용량
   - 메모리 사용량
   - CPU 사용률
   - 디스크 I/O

3. 품질 지표
   - 생성된 블로그 품질 점수
   - 중복 데이터 비율
   - 에러 발생 빈도

### 12.2 알림 설정
- 에러 발생 시 Slack 알림
- 리소스 사용량 임계치 초과 시 이메일 알림
- API 응답 시간 지연 시 로그 알림 