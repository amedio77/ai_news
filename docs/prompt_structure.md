# AI News Generator 프롬프트 구조

## 1. 프롬프트 설정 파일 구조 (`config/prompts.json`)

- 최상위 카테고리로 구분:
  - `news_analysis`
  - `content_generation`
  - `metadata`
- 각 카테고리는 다음을 포함:
  - `system` 프롬프트
  - 세부 작업별 프롬프트
- 모든 프롬프트에 `{tone_guidelines}` 변수를 통해 톤 가이드라인 주입

## 2. 프롬프트 로딩 메커니즘 (`GPTProcessor` 클래스)

```python
def _load_prompts(self) -> Dict[str, Any]:
    try:
        with open('config/prompts.json', 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        logging.info("Loaded prompts configuration from config/prompts.json")
        
        # 톤 가이드라인 로드
        tone_guidelines = self._load_tone_guidelines()
        if tone_guidelines:
            # 시스템 프롬프트에 톤 가이드라인 추가
```

## 3. 프롬프트 접근 방식

```python
def _load_prompt(self, prompt_path: str) -> Dict[str, str]:
    """프롬프트 설정 로드
    
    Args:
        prompt_path (str): 점(.)으로 구분된 프롬프트 경로 (예: 'content_generation.meta_description')
        
    Returns:
        Dict[str, str]: 프롬프트 설정
    """
    try:
        # 경로를 키로 분리
        keys = prompt_path.split('.')
        
        # 프롬프트 설정 가져오기
        prompt = self.prompts
        for key in keys:
            prompt = prompt[key]
        
        return prompt
```

## 4. 메시지 준비 프로세스

```python
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
```

## 5. 주요 프롬프트 유형

### news_analysis
- 뉴스 분석 및 트렌드 파악

### content_generation
- `news_blog_post_intro`: 도입부 (최소 1000자)
- `news_blog_post_trends`: 트렌드 분석 (최소 2000자)
- `news_blog_post_conclusion`: 결론 (최소 1200자)
- `meta_description`: SEO 메타 설명 (120-145자)

## 6. 톤 가이드라인 통합

- `_load_tone_guidelines()` 메서드를 통해 `tone_guidelines.txt`에서 로드
- 시스템 프롬프트에 자동으로 통합
- 포함 내용:
  - 응답 스타일
  - 정확성 가이드라인
  - 공감 규칙

## 7. 메타데이터 설정

### Temperature 설정
- 분석용: 0.4
- 블로그용: 0.7

### 최대 토큰 설정
- 분석용: 1000
- 블로그 포스트용: 4000
- 메타 설명용: 200

## 8. 프롬프트 참조 구조

### 파일 구조
```
ai_news/
├── config/
│   ├── prompts.json        # 실제 GPT 요청에 사용되는 프롬프트
│   └── tone_guidelines.txt # 톤 가이드라인 정의
├── docs/
│   ├── prompts/
│   │   └── blog_content.md # 프롬프트 작성 가이드라인 문서
│   └── prompt_structure.md # 전체 프롬프트 시스템 구조 설명
```

### 프롬프트 수정 프로세스

1. **프롬프트 수정 시 참고 파일**:
   - `config/prompts.json`: 실제 GPT API 호출에 사용되는 프롬프트
   - `docs/prompts/blog_content.md`: 프롬프트 작성 가이드라인
   - `src/processors/gpt_processor.py`: 프롬프트 처리 로직

2. **주요 수정 포인트**:
   - 길이 수정: `config/prompts.json`의 각 섹션별 프롬프트
   - 톤/스타일 수정: `config/prompts.json`의 system 프롬프트와 `config/tone_guidelines.txt`
   - 구조 수정: `docs/prompts/blog_content.md`와 `config/prompts.json`

### 톤 가이드라인 참조 구조

1. **톤 가이드라인 적용 과정**:
```python
def _load_prompts(self) -> Dict[str, Any]:
    try:
        with open('config/prompts.json', 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        logging.info("Loaded prompts configuration from config/prompts.json")
        
        # 톤 가이드라인 로드
        tone_guidelines = self._load_tone_guidelines()
        if tone_guidelines:
            # 시스템 프롬프트에 톤 가이드라인 추가
```

2. **톤 가이드라인 적용 방식**:
```json
{
  "content_generation": {
    "system": "Write in the following tone: {tone_guidelines}...",
    "news_blog_post_intro": "Following the tone guidelines...",
    "news_blog_post_trends": "Maintaining the established tone...",
    "news_blog_post_conclusion": "Consistent with the tone..."
  }
}
```

3. **톤 수정 시 체크포인트**:

   a. `config/tone_guidelines.txt` 수정
      - 글쓰기 스타일
      - 전문성 수준
      - 감정 톤
      - 용어 사용 지침

   b. `config/prompts.json` 확인
      - 시스템 프롬프트의 `{tone_guidelines}` 변수 위치
      - 각 섹션별 프롬프트의 톤 관련 지시사항

   c. `src/processors/gpt_processor.py` 확인
      - `_load_tone_guidelines()` 메서드
      - 톤 가이드라인 적용 로직

### 현재 설정된 길이 제한
- 도입부: 1000자
- 트렌드 분석: 2000자
- 결론: 1200자
- 메타 설명: 120-145자

## 장점

- 모듈화된 구조로 새로운 프롬프트 유형 추가 용이
- 톤 가이드라인을 통한 일관된 스타일 유지
- 명확한 설정 구조로 유지보수 용이 