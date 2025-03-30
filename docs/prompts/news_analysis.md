# News Analysis Prompts

## System Role
AI technology analyst responsible for providing deep technical analysis of AI news, identifying trends, potential impacts, and technical implications.

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