import uuid
from agents.base_agent import BaseAgent
from typing import Dict, Any

class RefactoringAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if agent_id is None:
            agent_id = f"refactoring_agent_{uuid.uuid4().hex[:8]}"
        super().__init__(agent_id, "refactoring")

    def handle_task(self, task_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        print(f"RefactoringAgent {self.agent_id} handling task type: {task_type} with details: {details}")
        
        if task_type == "refactor_code":
            code_snippet = details.get("code_snippet", "")
            if not code_snippet:
                return {"status": "error", "message": "No code snippet provided for refactoring."}

            try:
                refactoring_response = self._generate_llm_response(
                    prompt_template_name="refactor_code.txt",
                    placeholders={"CODE_SNIPPET": code_snippet}
                )
                return {"status": "success", "recommendation": refactoring_response}
            except Exception as e:
                return {"status": "error", "message": f"Error during Gemini refactoring: {e}"}
        
        return {"status": "error", "message": f"Unknown task type: {task_type} for RefactoringAgent."}

if __name__ == "__main__":
    agent = RefactoringAgent()
    agent.register_with_orchestrator()
    try:
        agent.start_consuming_tasks()
    except KeyboardInterrupt:
        print(f"RefactoringAgent {agent.agent_id} stopped.")
    finally:
        agent.close_connection()
