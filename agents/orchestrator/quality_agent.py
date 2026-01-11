import uuid
from agents.base_agent import BaseAgent
from typing import Dict, Any

class QualityAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if agent_id is None:
            agent_id = f"quality_agent_{uuid.uuid4().hex[:8]}"
        super().__init__(agent_id, "quality")

    def handle_task(self, task_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        print(f"QualityAgent {self.agent_id} handling task type: {task_type} with details: {details}")
        
        if task_type == "review_code":
            code_diff = details.get("code_diff", "")
            if not code_diff:
                return {"status": "error", "message": "No code diff provided for quality review."}

            try:
                review_response = self._generate_llm_response(
                    prompt_template_name="review_quality.txt",
                    placeholders={"CODE_DIFF": code_diff}
                )
                return {"status": "success", "review": review_response}
            except Exception as e:
                return {"status": "error", "message": f"Error during Gemini quality review: {e}"}
        
        return {"status": "error", "message": f"Unknown task type: {task_type} for QualityAgent."}

if __name__ == "__main__":
    agent = QualityAgent()
    agent.register_with_orchestrator()
    try:
        agent.start_consuming_tasks()
    except KeyboardInterrupt:
        print(f"QualityAgent {agent.agent_id} stopped.")
    finally:
        agent.close_connection()
