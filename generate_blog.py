import os
import sys
from dotenv import load_dotenv
from src.processors.gpt_processor import GPTProcessor
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # 환경 변수 로드
        load_dotenv()
        
        # OpenAI API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        # GPTProcessor 초기화
        processor = GPTProcessor(api_key)

        # 뉴스 파일 경로 설정
        news_file = 'data/crawled/test_news.json'
        if not os.path.exists(news_file):
            raise FileNotFoundError(f"뉴스 파일을 찾을 수 없습니다: {news_file}")

        logger.info(f"블로그 생성 시작: {news_file}")

        # 블로그 포스트 생성
        content, meta_description = processor.generate_blog_post(news_file)

        # 결과 출력
        print("\n=== 생성된 블로그 포스트 ===")
        print(content)
        print("\n=== 메타 설명 ===")
        print(meta_description)

        logger.info("블로그 생성 완료")

    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 