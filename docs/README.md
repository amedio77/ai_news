# AI News Generator

AI 뉴스 생성 및 WordPress 자동 게시 시스템

## 프로젝트 구조

```
ai_news/
├── src/
│   ├── core/
│   │   ├── config.py        # 설정 관리
│   │   └── utils.py         # 유틸리티 함수
│   ├── media/
│   │   ├── image_generator.py   # 이미지 생성
│   │   └── image_processor.py   # 이미지 처리
│   └── integrations/
│       ├── wordpress/
│       │   ├── media_manager.py # WordPress 미디어 관리
│       │   └── publisher.py     # WordPress 게시
│       └── gpt/
│           └── blog_generator.py # 블로그 생성
├── output/
│   ├── blogs/               # 생성된 블로그
│   ├── images/              # 생성된 이미지
│   └── metadata/           # 메타데이터
├── tests/                  # 테스트 코드
├── docs/                   # 문서
├── .env.example           # 환경 변수 예시
├── requirements.txt       # 의존성 패키지
└── README.md             # 프로젝트 설명
```

## 설치 방법

1. Python 3.8 이상 설치

2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
- `.env.example` 파일을 `.env`로 복사
- 필요한 API 키와 설정 값 입력

## 환경 변수

```env
# OpenAI API
OPENAI_API_KEY=your_api_key

# WordPress
WP_URL=your_wordpress_url
WP_USERNAME=your_username
WP_PASSWORD=your_password
```

## 사용 방법

### 1. 블로그 생성

```python
from src.gpt.blog_generator import GPTBlogGenerator

generator = GPTBlogGenerator()
blog_path = generator.generate_blog()
```

### 2. 이미지 생성

```python
from src.media.image_generator import ImageGenerator

generator = ImageGenerator()
image_path = generator.generate_image(
    prompt="AI technology concept",
    filename="ai_concept.png"
)
```

### 3. WordPress 게시

```python
from src.wordpress.publisher import WordPressPublisher

publisher = WordPressPublisher()
post_url = publisher.publish_blog(
    file_path="output/blogs/ai_blog.md",
    categories=["AI", "Technology"],
    tags=["AI", "News", "Tech"],
    status="draft"
)
```

## 주요 기능

### 이미지 생성
- DALL-E 3를 사용한 고품질 이미지 생성
- 이미지 최적화 및 메타데이터 관리
- 샘플 이미지 자동 생성 기능

### WordPress 통합
- 마크다운 형식의 블로그를 WordPress HTML로 변환
- 이미지 자동 업로드 및 최적화
- 게시물 카테고리 및 태그 관리

### 유틸리티
- 파일 및 메타데이터 관리
- 에러 처리 및 로깅
- 설정 관리

## 라이선스

MIT License
