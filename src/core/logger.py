import logging
import json
from datetime import datetime
from pathlib import Path

class GPTLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 일반 로그 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # GPT 사용량 로그 파일 설정
        self.usage_log_file = self.log_dir / f"gpt_usage_{datetime.now().strftime('%Y%m%d')}.json"
        self.usage_data = self._load_usage_data()
        
        # GPT 모델별 가격 (1K 토큰당 USD)
        self.price_rates = {
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }
    
    def _load_usage_data(self):
        if self.usage_log_file.exists():
            with open(self.usage_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "sessions": [],
            "total_tokens": 0,
            "total_cost": 0,
            "model_usage": {}
        }
    
    def log_gpt_usage(self, session_id, model_name, prompt_tokens, completion_tokens, task_type):
        """GPT API 사용량 로깅
        
        Args:
            session_id (str): 세션 ID (블로그 포스트 ID 등)
            model_name (str): 사용된 GPT 모델명
            prompt_tokens (int): 입력 토큰 수
            completion_tokens (int): 출력 토큰 수
            task_type (str): 작업 유형 (예: blog_generation, image_prompt 등)
        """
        # 비용 계산
        rates = self.price_rates.get(model_name, {"input": 0, "output": 0})
        prompt_cost = (prompt_tokens / 1000) * rates["input"]
        completion_cost = (completion_tokens / 1000) * rates["output"]
        total_cost = prompt_cost + completion_cost
        
        # 세션 데이터 생성
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "model": model_name,
            "task_type": task_type,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost": total_cost
        }
        
        # 사용량 데이터 업데이트
        self.usage_data["sessions"].append(session_data)
        self.usage_data["total_tokens"] += (prompt_tokens + completion_tokens)
        self.usage_data["total_cost"] += total_cost
        
        # 모델별 사용량 업데이트
        if model_name not in self.usage_data["model_usage"]:
            self.usage_data["model_usage"][model_name] = {
                "total_tokens": 0,
                "total_cost": 0,
                "tasks": {}
            }
        
        model_usage = self.usage_data["model_usage"][model_name]
        model_usage["total_tokens"] += (prompt_tokens + completion_tokens)
        model_usage["total_cost"] += total_cost
        
        if task_type not in model_usage["tasks"]:
            model_usage["tasks"][task_type] = {
                "count": 0,
                "total_tokens": 0,
                "total_cost": 0
            }
        
        task_data = model_usage["tasks"][task_type]
        task_data["count"] += 1
        task_data["total_tokens"] += (prompt_tokens + completion_tokens)
        task_data["total_cost"] += total_cost
        
        # 로그 파일 저장
        self._save_usage_data()
        
        # 콘솔에 로그 출력
        self.logger.info(
            f"GPT Usage - Model: {model_name}, Task: {task_type}, "
            f"Tokens: {prompt_tokens + completion_tokens}, Cost: ${total_cost:.4f}"
        )
    
    def _save_usage_data(self):
        """사용량 데이터를 JSON 파일로 저장"""
        with open(self.usage_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage_data, f, ensure_ascii=False, indent=2)
    
    def get_usage_summary(self):
        """사용량 요약 정보 반환"""
        return {
            "total_tokens": self.usage_data["total_tokens"],
            "total_cost": self.usage_data["total_cost"],
            "model_usage": self.usage_data["model_usage"]
        }
    
    def print_cost_summary(self):
        """비용 요약 정보 출력"""
        summary = self.get_usage_summary()
        
        print("\n=== GPT 사용량 및 비용 요약 ===")
        print(f"총 토큰 사용량: {summary['total_tokens']:,}")
        print(f"총 비용: ${summary['total_cost']:.4f}")
        
        print("\n=== 모델별 사용량 ===")
        for model, usage in summary["model_usage"].items():
            print(f"\n[{model}]")
            print(f"- 총 토큰: {usage['total_tokens']:,}")
            print(f"- 총 비용: ${usage['total_cost']:.4f}")
            
            print("\n작업별 통계:")
            for task, task_data in usage["tasks"].items():
                print(f"  {task}:")
                print(f"  - 실행 횟수: {task_data['count']}")
                print(f"  - 총 토큰: {task_data['total_tokens']:,}")
                print(f"  - 총 비용: ${task_data['total_cost']:.4f}")
                if task_data['count'] > 0:
                    avg_cost = task_data['total_cost'] / task_data['count']
                    print(f"  - 평균 비용: ${avg_cost:.4f}/회") 