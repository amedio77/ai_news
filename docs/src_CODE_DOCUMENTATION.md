"""
코드 문서화: AI 뉴스 블로그 자동화 프로그램

이 파일은 AI 뉴스 블로그 자동화 프로그램의 코드 문서화를 제공합니다.
각 모듈과 주요 클래스, 함수에 대한 설명을 포함합니다.
"""

# 1. 크롤러 모듈 (crawler/)

## twitter_crawler.py
"""
Twitter API를 활용하여 AI 관련 뉴스를 크롤링하는 모듈입니다.
주요 클래스: TwitterNewsCrawler

주요 기능:
- Twitter API를 통한 AI 관련 키워드 검색
- 트윗 데이터에서 뉴스 정보 추출
- API 연결 실패 시 샘플 데이터 생성
- 수집된 뉴스 데이터 저장
"""

## news_processor.py
"""
크롤링된 뉴스 데이터를 정제하는 모듈입니다.
주요 클래스: NewsProcessor

주요 기능:
- 트윗 텍스트 정제 (URL 제거, 해시태그 정리 등)
- URL 추출
- 정제된 데이터 저장
"""

# 2. GPT 통합 모듈 (gpt_integration/)

## blog_generator.py
"""
OpenAI GPT를 활용하여 AI 관련 뉴스로부터 한글 블로그를 생성하는 모듈입니다.
주요 클래스: GPTBlogGenerator

주요 기능:
- 뉴스 데이터 로드
- GPT 프롬프트 준비
- OpenAI API를 통한 블로그 생성
- API 연결 실패 시 샘플 블로그 생성
- 생성된 블로그 저장
"""

# 3. 워드프레스 통합 모듈 (wordpress_integration/)

## wordpress_publisher.py
"""
생성된 블로그를 워드프레스에 게시하는 모듈입니다.
주요 클래스: WordPressPublisher

주요 기능:
- 워드프레스 API 연결
- 블로그 내용 로드
- 마크다운을 HTML로 변환
- 워드프레스에 블로그 게시
- 연결 실패 시 게시 시뮬레이션
"""

# 4. 자동화 스크립트 (automate.py)

"""
전체 워크플로우를 자동화하는 스크립트입니다.
주요 클래스: AINewsBlogAutomation

주요 기능:
- 뉴스 크롤러 실행
- 뉴스 데이터 처리기 실행
- 블로그 생성기 실행
- 워드프레스 게시기 실행
- 전체 워크플로우 실행
- 워크플로우 스케줄링
- 명령줄 인자 처리
"""

# 5. 디렉토리 구조

"""
ai_news_blog/
├── crawler/                # 뉴스 크롤링 관련 코드
│   ├── twitter_crawler.py  # Twitter API 크롤러
│   └── news_processor.py   # 뉴스 데이터 처리기
├── gpt_integration/        # GPT 통합 관련 코드
│   └── blog_generator.py   # 블로그 생성기
├── wordpress_integration/  # 워드프레스 통합 관련 코드
│   └── wordpress_publisher.py  # 워드프레스 게시기
├── data/                   # 크롤링 및 처리된 데이터 저장 디렉토리
├── output/                 # 생성된 블로그 저장 디렉토리
├── automate.py             # 자동화 스크립트
├── .env                    # 환경 설정 파일
└── README.md               # 프로젝트 설명
"""

# 6. 데이터 흐름

"""
1. 뉴스 크롤링: Twitter API를 통해 AI 관련 뉴스 수집
   - 입력: AI 키워드 (.env 파일에 설정)
   - 출력: JSON 형식의 뉴스 데이터 (data/ai_news_*.json)

2. 데이터 처리: 크롤링된 뉴스 데이터 정제
   - 입력: 크롤링된 뉴스 데이터 (data/ai_news_*.json)
   - 출력: 정제된 뉴스 데이터 (data/processed_ai_news_*.json)

3. 블로그 생성: GPT를 활용하여 한글 블로그 생성
   - 입력: 정제된 뉴스 데이터 (data/processed_ai_news_*.json)
   - 출력: 마크다운 형식의 블로그 (output/ai_blog_*.md)

4. 워드프레스 게시: 생성된 블로그를 워드프레스에 게시
   - 입력: 마크다운 형식의 블로그 (output/ai_blog_*.md)
   - 출력: 워드프레스에 게시된 블로그 또는 시뮬레이션 결과 (output/wordpress_simulation_result.txt)
"""

# 7. 오류 처리

"""
- Twitter API 연결 실패: 샘플 데이터 생성으로 대체
- OpenAI API 연결 실패: 샘플 블로그 생성으로 대체
- 워드프레스 연결 실패: 게시 시뮬레이션으로 대체
- 로깅: 모든 단계에서 로그 기록 (ai_news_blog.log)
"""

# 8. 확장 가능성

"""
- 추가 뉴스 소스 통합: 다른 소셜 미디어 또는 뉴스 사이트 크롤링 기능 추가
- 다국어 지원: 다양한 언어로 블로그 생성 기능 확장
- 이미지 생성: AI 이미지 생성 API를 통한 블로그 이미지 자동 생성
- 분석 기능: 게시된 블로그의 성과 분석 기능 추가
"""
