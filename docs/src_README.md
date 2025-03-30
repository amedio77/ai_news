# AI 뉴스 블로그 자동화 프로그램 사용 설명서

## 개요

이 프로그램은 해외 AI 관련 최신 뉴스를 자동으로 크롤링하여 GPT에 전송하고, 한글 블로그를 생성한 후 워드프레스에 게시하는 자동화 솔루션입니다. 뉴스 수집부터 블로그 게시까지 전체 과정을 자동화하여 AI 기술 동향에 관한 블로그를 효율적으로 운영할 수 있습니다.

## 설치 방법

### 시스템 요구사항

- Python 3.6 이상
- 인터넷 연결
- 워드프레스 사이트 (선택적)

### 설치 단계

1. 저장소 클론 또는 다운로드:
   ```bash
   git clone https://github.com/yourusername/ai-news-blog.git
   cd ai-news-blog
   ```

2. 필요한 패키지 설치:
   ```bash
   pip install requests python-dotenv openai python-wordpress-xmlrpc beautifulsoup4
   ```

## 환경 설정

1. `.env` 파일 설정:
   - 프로젝트 루트 디렉토리에 있는 `.env.example` 파일을 `.env`로 복사합니다.
   ```bash
   cp .env.example .env
   ```
   
   - `.env` 파일을 열고 다음 설정을 입력합니다:
   ```
   # OpenAI API 설정
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4

   # 워드프레스 설정
   WP_URL=https://your-wordpress-site.com/xmlrpc.php
   WP_USERNAME=your_wordpress_username
   WP_PASSWORD=your_wordpress_password

   # 뉴스 크롤링 설정
   AI_KEYWORDS=artificial intelligence,machine learning,deep learning,neural networks,AI,GPT,LLM
   NEWS_LIMIT=10
   ```

2. OpenAI API 키 발급:
   - [OpenAI 웹사이트](https://platform.openai.com/)에서 계정을 생성하고 API 키를 발급받습니다.
   - 발급받은 API 키를 `.env` 파일의 `OPENAI_API_KEY` 항목에 입력합니다.

3. 워드프레스 설정 (선택적):
   - 워드프레스 사이트가 있는 경우, XML-RPC 기능이 활성화되어 있는지 확인합니다.
   - 워드프레스 사이트 URL, 사용자 이름, 비밀번호를 `.env` 파일에 입력합니다.

## 사용 방법

### 전체 워크플로우 실행

전체 워크플로우(뉴스 크롤링, 블로그 생성, 워드프레스 게시)를 한 번에 실행하려면:

```bash
python automate.py
```

### 특정 단계만 실행

특정 단계만 실행하려면 `--step` 옵션을 사용합니다:

```bash
# 뉴스 크롤링만 실행
python automate.py --step crawler

# 블로그 생성만 실행
python automate.py --step generator

# 워드프레스 게시만 실행
python automate.py --step publisher
```

### 스케줄링 실행

정기적으로 자동 실행하려면 `--schedule` 옵션을 사용합니다:

```bash
# 24시간마다 자동 실행
python automate.py --schedule 24

# 12시간마다 자동 실행
python automate.py --schedule 12
```

## 주요 기능 설명

### 1. 뉴스 크롤링 (crawler)

- Twitter API를 활용하여 AI 관련 최신 뉴스를 수집합니다.
- 설정된 키워드(`AI_KEYWORDS`)를 기반으로 검색합니다.
- API 연결 실패 시 샘플 데이터를 생성하여 워크플로우가 중단되지 않도록 합니다.
- 수집된 데이터는 `data` 디렉토리에 JSON 형식으로 저장됩니다.

### 2. 데이터 처리 (processor)

- 크롤링된 뉴스 데이터를 정제합니다.
- URL 추출, 텍스트 정리 등의 작업을 수행합니다.
- 처리된 데이터는 `data` 디렉토리에 저장됩니다.

### 3. 블로그 생성 (generator)

- OpenAI GPT를 활용하여 수집된 뉴스를 기반으로 한글 블로그를 생성합니다.
- 블로그는 제목, 도입부, 본문, 결론 구조를 갖습니다.
- API 연결 실패 시 샘플 블로그를 생성하여 워크플로우가 중단되지 않도록 합니다.
- 생성된 블로그는 `output` 디렉토리에 마크다운 형식으로 저장됩니다.

### 4. 워드프레스 게시 (publisher)

- 생성된 블로그를 워드프레스에 자동으로 게시합니다.
- 마크다운을 HTML로 변환하여 워드프레스에 적합한 형식으로 변환합니다.
- 카테고리와 태그를 자동으로 설정합니다.
- 워드프레스 연결 실패 시 게시 시뮬레이션을 실행하여 워크플로우가 중단되지 않도록 합니다.

## 디렉토리 구조

```
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
```

## 문제 해결

### API 연결 문제

- OpenAI API 연결 오류: API 키가 올바른지 확인하고, 필요한 경우 `.env` 파일에서 모델을 변경합니다.
- 워드프레스 연결 오류: 워드프레스 사이트 URL, 사용자 이름, 비밀번호가 올바른지 확인하고, XML-RPC 기능이 활성화되어 있는지 확인합니다.

### 실행 오류

- 패키지 설치 오류: `pip install -r requirements.txt`를 실행하여 필요한 모든 패키지를 설치합니다.
- 권한 오류: 스크립트에 실행 권한이 있는지 확인합니다. `chmod +x automate.py`를 실행하여 권한을 부여할 수 있습니다.

## 커스터마이징

### 크롤링 키워드 변경

`.env` 파일에서 `AI_KEYWORDS` 항목을 수정하여 크롤링할 키워드를 변경할 수 있습니다.

### 블로그 생성 프롬프트 변경

`gpt_integration/blog_generator.py` 파일에서 `prepare_prompt` 메서드를 수정하여 블로그 생성 프롬프트를 변경할 수 있습니다.

### 워드프레스 카테고리 및 태그 변경

`wordpress_integration/wordpress_publisher.py` 파일에서 `publish_blog` 메서드의 `post.terms_names` 부분을 수정하여 카테고리와 태그를 변경할 수 있습니다.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 연락처

문제나 제안사항이 있으면 [이메일 주소]로 연락해 주세요.
