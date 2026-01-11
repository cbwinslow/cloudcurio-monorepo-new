import uuid
from agents.base_agent import BaseAgent
from typing import Dict, Any

class OpencodeAgent(BaseAgent):
    def __init__(self, agent_id: str = None):
        if agent_id is None:
            agent_id = f"opencode_agent_{uuid.uuid4().hex[:8]}"
        super().__init__(agent_id, "opencode")

    def handle_task(self, task_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        print(f"OpencodeAgent {self.agent_id} handling task type: {task_type} with details: {details}")
        
        if task_type == "general_task":
            task_description = details.get("task_description", "")
            if not task_description:
                return {"status": "error", "message": "No task description provided for Opencode agent."}

            try:
                opencode_response = self._generate_llm_response(
                    prompt_template_name="general_task.txt",
                    placeholders={"TASK_DESCRIPTION": task_description}
                )
                return {"status": "success", "output": opencode_response}
            except Exception as e:
                return {"status": "error", "message": f"Error during Opencode agent task: {e}"}
        
        # Potentially add other task types here for direct command execution etc.
        # elif task_type == "execute_command":
        #     command = details.get("command", "")
        #     if command:
        #         try:
        #             result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True)
        #             return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
        #         except subprocess.CalledProcessError as e:
        #             return {"status": "error", "stdout": e.stdout, "stderr": e.stderr}
        #     return {"status": "error", "message": "No command provided for execution."}

        return {"status": "error", "message": f"Unknown task type: {task_type} for OpencodeAgent."}

if __name__ == "__main__":
    agent = OpencodeAgent()
    agent.register_with_orchestrator()
    try:
        agent.start_consuming_tasks()
    except KeyboardInterrupt:
        print(f"OpencodeAgent {agent.agent_id} stopped.")
    finally:
        agent.close_connection()
