# Content Generation Prompts

## System Role
AI technology content creator, specializing in creating engaging and informative content about artificial intelligence news and developments.

## News Blog Post
Used to create comprehensive blog posts based on trend and technical analyses.

### Parameters
- Temperature: 0.7
- Max Tokens: 2000

### Prompt Template
```
Create a comprehensive blog post based on the trend and technical analyses of recent AI news. Requirements:
1. SEO-optimized title with focus keywords
2. 4000-6000 word length
3. 8-10 sections with 200-300 words each
4. Include data and statistics for credibility
5. Technical accuracy balanced with accessibility
6. Clear structure: intro, trend analysis, technical deep-dive, implications, conclusion

Trend analysis:
{trend_analysis}

Technical analysis:
{tech_analysis}
```

## Meta Description
Used to create SEO-optimized meta descriptions for blog posts.

### Parameters
- Temperature: 0.7
- Max Tokens: 200

### Prompt Template
```
Create an SEO-optimized meta description (150-160 characters) for this AI news analysis blog post. Include key trends and encourage clicks:

Post title:
{post_title}

Post content:
{post_content}
```

## Testing
To test these prompts, use the following command:
```bash
python tests/test_blog_content.py -v -s
```

The test will:
1. Generate blog post from trend and technical analyses
2. Generate meta description
3. Verify the outputs meet length and structure requirements
4. Check for required sections and SEO elements 