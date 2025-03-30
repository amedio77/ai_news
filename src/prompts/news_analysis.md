# 뉴스 분석 프롬프트

## 개요
이 프롬프트는 AI 기술 뉴스 분석과 트렌드 파악에 사용됩니다.

## 프롬프트
```json
{
  "system": "당신은 AI 기술 분야의 전문 분석가입니다. 각 뉴스의 출처를 [출처: 출처명, 날짜: YYYY-MM-DD] 형식으로 명확히 인용해야 합니다. 모든 통계, 데이터, 전문가 의견은 출처를 반드시 표시해야 합니다.",
  "trend_analysis": "다음 뉴스 기사들을 분석하여 AI 기술 발전의 주요 트렌드와 패턴을 파악해주세요. 각 뉴스는 제공된 날짜 정보를 그대로 인용해주세요:\n\n{news_data}\n\n다음 항목들을 중심으로 분석을 제공해주세요:\n1. 주요 뉴스 요약 (각 요약마다 [출처: 출처명, 날짜: YYYY-MM-DD] 형식으로 표기)\n2. 기술적 진보 분석 (관련 뉴스 날짜 포함)\n3. 산업 영향 분석 (관련 기업/기관 명시)\n4. 새로운 트렌드 (근거가 되는 뉴스 날짜 포함)\n5. 향후 전망 (분석의 근거가 된 날짜 명시)\n\n모든 분석은 구체적인 출처와 날짜를 포함해야 하며, 통계나 데이터 인용 시에도 출처를 명시해야 합니다."
}
```

## 사용 가이드라인
1. 모든 뉴스 인용시 날짜를 정확히 표기
2. 기술적 분석과 산업 영향을 구분하여 설명
3. 각 분석에 대한 근거를 명확히 제시
4. 향후 전망은 구체적인 데이터 기반으로 작성

## Trend Analysis
Used to analyze multiple AI news articles and identify key trends and patterns.

### Parameters
- Temperature: 0.4
- Max Tokens: 1000

### Prompt Template
```
Analyze the following AI news articles and identify key trends and patterns. Consider:
1. Major technological developments
2. Industry shifts and innovations
3. Market impacts and business implications
4. Emerging patterns and future directions

News articles:
{news_data}
```

## Technical Analysis
Used to provide technical deep-dive based on the trend analysis.

### Parameters
- Temperature: 0.4
- Max Tokens: 1000

### Prompt Template
```
Based on the trend analysis, provide a technical deep-dive into the key developments. Focus on:
1. Technical innovations and breakthroughs
2. Implementation challenges and solutions
3. Impact on existing AI systems and frameworks
4. Future technical implications

Trend analysis:
{trend_analysis}
```

## Testing
To test these prompts, use the following command:
```bash
python tests/test_blog_content.py -v -s
```

The test will:
1. Load sample news data
2. Generate trend analysis
3. Generate technical analysis
4. Verify the outputs contain required information 