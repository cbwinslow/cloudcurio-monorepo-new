import pika
import uuid
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os # Import os for environment variables

from agents.communication import (
    get_rabbitmq_connection, declare_exchanges, send_message, consume_messages,
    AgentMessage, TASK_EXCHANGE, RESULT_EXCHANGE, VOTE_EXCHANGE
)
from agents.llm_utils import load_prompt_template, generate_gemini_response # Import LLM utilities

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str, orchestrator_id: str = "orchestrator_1"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.orchestrator_id = orchestrator_id
        self.connection = get_rabbitmq_connection()
        self.channel = self.connection.channel()
        declare_exchanges(self.channel) # Ensure exchanges are declared

        # Declare a unique queue for this agent to receive tasks
        self.task_queue = f"{self.agent_id}_task_queue"
        self.channel.queue_declare(queue=self.task_queue, durable=True)
        self.channel.queue_bind(
            exchange=TASK_EXCHANGE,
            queue=self.task_queue,
            routing_key=self.agent_id # Agent listens for messages routed to its ID
        )
        print(f"Agent {self.agent_id} ({self.agent_type}) ready and listening on {self.task_queue}")

    def register_with_orchestrator(self):
        """Sends a message to the orchestrator indicating agent is ready."""
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=self.orchestrator_id,
            message_type="AGENT_READY",
            payload={"agent_type": self.agent_type}
        )
        send_message(self.channel, message, exchange=RESULT_EXCHANGE, routing_key=self.orchestrator_id)
        print(f"Agent {self.agent_id} registered with orchestrator.")

    def send_results(self, task_id: str, payload: Dict[str, Any]):
        """Sends task results back to the orchestrator."""
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=self.orchestrator_id,
            message_type="RESULT",
            task_id=task_id,
            payload=payload
        )
        send_message(self.channel, message, exchange=RESULT_EXCHANGE, routing_key=self.orchestrator_id)
        print(f"Agent {self.agent_id} sent results for task {task_id}.")

    def send_vote(self, task_id: str, vote: Any, vote_topic: str):
        """Sends a vote on a specific topic."""
        message = AgentMessage(
            sender_id=self.agent_id,
            message_type="VOTE",
            task_id=task_id,
            payload={"vote_topic": vote_topic, "vote": vote}
        )
        send_message(self.channel, message, exchange=VOTE_EXCHANGE, routing_key=f"vote.{vote_topic}")
        print(f"Agent {self.agent_id} cast vote '{vote}' on topic '{vote_topic}' for task {task_id}.")

    def _process_task_message(self, ch, method, properties, body):
        """Internal callback for processing incoming task messages."""
        message = AgentMessage.from_json(body.decode())
        print(f" [x] Agent {self.agent_id} received task {message.task_id} of type {message.payload.get('type')}")
        
        # Acknowledge the message immediately to prevent redelivery
        ch.basic_ack(method.delivery_tag)

        # Process the task (abstract method to be implemented by subclasses)
        results = self.handle_task(message.payload.get('type'), message.payload.get('details'))
        
        # Send results back to orchestrator
        self.send_results(message.payload["task_id"], results)

    def start_consuming_tasks(self):
        """Starts consuming task messages from its queue."""
        self.channel.basic_consume(
            queue=self.task_queue,
            on_message_callback=self._process_task_message,
            auto_ack=False
        )
        print(f"Agent {self.agent_id} is now consuming tasks...")
        self.channel.start_consuming()

    def close_connection(self):
        """Closes the RabbitMQ connection."""
        self.connection.close()
        print(f"Agent {self.agent_id} RabbitMQ connection closed.")

    @abstractmethod
    def handle_task(self, task_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Abstract method to be implemented by specialized agents to handle tasks."""
        pass

    def _generate_llm_response(self, prompt_template_name: str, placeholders: Dict[str, str]) -> str:
        """Helper to generate LLM responses using Gemini."""
        prompt_template = load_prompt_template(prompt_template_name)
        prompt = prompt_template
        for key, value in placeholders.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", value)
        return generate_gemini_response(prompt)


# Example of a specialized agent (for testing purposes)
class ExampleAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "example_agent")

    def handle_task(self, task_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        print(f"ExampleAgent {self.agent_id} handling task type: {task_type} with details: {details}")
        # Simulate some work
        time.sleep(2) 
        
        # Example of using LLM utility
        if task_type == "generate_idea":
            prompt_template = load_prompt_template("generate_idea.txt") # Assuming such a template exists
            idea = generate_gemini_response(prompt_template.replace("{{TOPIC}}", details.get("topic", "general")))
            return {"status": "success", "idea": idea}

        return {"status": "success", "agent_response": f"Processed {task_type} with {details}"}

if __name__ == "__main__":
    agent_id = str(uuid.uuid4())
    example_agent = ExampleAgent(agent_id)
    example_agent.register_with_orchestrator()
    print(f"Example Agent {agent_id} started. Press CTRL+C to exit.")
    try:
        example_agent.start_consuming_tasks()
    except KeyboardInterrupt:
        print("Example Agent stopped by user.")
    finally:
        example_agent.close_connection()
