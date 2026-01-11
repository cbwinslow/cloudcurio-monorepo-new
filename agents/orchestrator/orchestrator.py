import uuid
import time
import json
import pika
from typing import Dict, Any, List
import os

from agents.communication import (
    get_rabbitmq_connection, declare_exchanges, send_message, consume_messages,
    AgentMessage, TASK_EXCHANGE, RESULT_EXCHANGE, VOTE_EXCHANGE, BROADCAST_EXCHANGE
)

class Orchestrator:
    def __init__(self, orchestrator_id: str = "orchestrator_1"):
        self.orchestrator_id = orchestrator_id
        self.connection = get_rabbitmq_connection()
        self.channel = self.connection.channel()
        declare_exchanges(self.channel)
        
        # Queue for results from agents
        self.results_queue = f"{self.orchestrator_id}_results_queue"
        self.channel.queue_declare(queue=self.results_queue, durable=True)
        self.channel.queue_bind(
            exchange=RESULT_EXCHANGE,
            queue=self.results_queue,
            routing_key=self.orchestrator_id
        )
        print(f"Orchestrator {self.orchestrator_id} listening on {self.results_queue}")

        # Queue for votes from agents
        self.vote_queue = f"{self.orchestrator_id}_vote_queue"
        self.channel.queue_declare(queue=self.vote_queue, durable=True)
        self.channel.queue_bind(
            exchange=VOTE_EXCHANGE,
            queue=self.vote_queue,
            routing_key="vote.*" # Listen to all vote topics
        )
        print(f"Orchestrator {self.orchestrator_id} listening for votes on {self.vote_queue}")

        self.agents: Dict[str, Any] = {} # To keep track of spawned agents
        self.tasks: Dict[str, Any] = {}  # To keep track of assigned tasks
        self.active_votes: Dict[str, Dict[str, Dict[str, Any]]] = {} # vote_topic -> task_id -> {"voted_agents": [], "votes": []}

    def spawn_agent(self, agent_id: str, agent_type: str):
        """Simulates spawning an agent and registers it."""
        self.agents[agent_id] = {"type": agent_type, "status": "idle"}
        print(f"Agent {agent_id} of type {agent_type} spawned and registered.")
        # In a real scenario, this would involve starting a new process for the agent

    def assign_task(self, agent_id: str, task_payload: Dict[str, Any], task_type: str = "review"):
        """Assigns a task to a specific agent."""
        task_id = str(uuid.uuid4())
        message = AgentMessage(
            sender_id=self.orchestrator_id,
            receiver_id=agent_id,
            message_type="TASK",
            payload={"task_id": task_id, "type": task_type, "details": task_payload}
        )
        send_message(self.channel, message, exchange=TASK_EXCHANGE, routing_key=agent_id)
        self.tasks[task_id] = {"agent_id": agent_id, "status": "assigned", "results": None}
        print(f"Task {task_id} assigned to agent {agent_id}.")
        return task_id

    def collect_results(self, ch, method, properties, body):
        """Callback for collecting results from agents."""
        message = AgentMessage.from_json(body.decode())
        print(f" [x] Received result for task {message.task_id} from agent {message.sender_id}")
        
        if message.task_id in self.tasks:
            self.tasks[message.task_id]["status"] = "completed"
            self.tasks[message.task_id]["results"] = message.payload
            print(f"Results for task {message.task_id} collected.")
        else:
            print(f"Warning: Received result for unknown task {message.task_id}")
        ch.basic_ack(method.delivery_tag)

    def initiate_vote(self, task_id: str, vote_topic: str, options: List[str]):
        """Initiates a voting process among relevant agents."""
        # This would typically broadcast a vote request
        message = AgentMessage(
            sender_id=self.orchestrator_id,
            message_type="VOTE_REQUEST",
            payload={"task_id": task_id, "topic": vote_topic, "options": options}
        )
        send_message(self.channel, message, exchange=BROADCAST_EXCHANGE) # Broadcast for now
        print(f"Vote initiated for task {task_id} on topic '{vote_topic}'.")

    def coordinate_consensus(self, vote_topic: str, task_id: str) -> Dict[str, Any]:
        """Coordinates the consensus based on collected votes for a specific topic and task."""
        if vote_topic not in self.active_votes or task_id not in self.active_votes[vote_topic]:
            return {"status": "no_votes", "message": f"No votes found for topic '{vote_topic}' and task '{task_id}'."}

        votes_data = self.active_votes[vote_topic][task_id]["votes"]
        
        if not votes_data:
            return {"status": "no_votes", "message": f"No votes recorded for topic '{vote_topic}' and task '{task_id}'."}

        # Example simple majority consensus
        # Assuming votes are simple strings or integers
        vote_counts = {}
        for vote in votes_data:
            vote_str = str(vote) # Ensure comparability
            vote_counts[vote_str] = vote_counts.get(vote_str, 0) + 1
        
        if not vote_counts:
            return {"status": "no_votes", "message": "No valid votes to aggregate."}

        # Find the most common vote(s)
        max_votes = 0
        winning_votes = []
        for vote, count in vote_counts.items():
            if count > max_votes:
                max_votes = count
                winning_votes = [vote]
            elif count == max_votes:
                winning_votes.append(vote)
        
        consensus_result = {
            "vote_topic": vote_topic,
            "task_id": task_id,
            "total_votes": len(votes_data),
            "vote_counts": vote_counts,
            "consensus": None,
            "message": ""
        }

        if len(winning_votes) == 1:
            consensus_result["consensus"] = winning_votes[0]
            consensus_result["message"] = f"Consensus reached: Majority voted for '{winning_votes[0]}'."
            consensus_result["status"] = "success"
        else:
            consensus_result["consensus"] = winning_votes # Multiple winners, no clear majority
            consensus_result["message"] = f"No clear majority. Multiple top votes: {', '.join(winning_votes)}."
            consensus_result["status"] = "tie"
        
        print(f"Consensus for topic '{vote_topic}' and task '{task_id}': {consensus_result['message']}")
        return consensus_result

    def _process_vote_message(self, ch, method, properties, body):
        """Callback for processing incoming vote messages."""
        message = AgentMessage.from_json(body.decode())
        vote_topic = message.payload.get("vote_topic")
        task_id = message.task_id
        vote = message.payload.get("vote")

        print(f" [x] Received vote '{vote}' on topic '{vote_topic}' for task {task_id} from agent {message.sender_id}")

        if vote_topic not in self.active_votes:
            self.active_votes[vote_topic] = {}
        if task_id not in self.active_votes[vote_topic]:
            self.active_votes[vote_topic][task_id] = {"voted_agents": [], "votes": []}
        
        if message.sender_id not in self.active_votes[vote_topic][task_id]["voted_agents"]:
            self.active_votes[vote_topic][task_id]["voted_agents"].append(message.sender_id)
            self.active_votes[vote_topic][task_id]["votes"].append(vote)
            print(f"Recorded vote from {message.sender_id} for task {task_id}.")
        else:
            print(f"Warning: Agent {message.sender_id} already voted for task {task_id} on topic {vote_topic}.")
        
        ch.basic_ack(method.delivery_tag)

    def start_listening(self):
        """Starts consuming messages from results and vote queues."""
        self.channel.basic_consume(
            queue=self.results_queue,
            on_message_callback=self.collect_results,
            auto_ack=False
        )
        self.channel.basic_consume(
            queue=self.vote_queue,
            on_message_callback=self._process_vote_message,
            auto_ack=False
        )
        print(f"Orchestrator {self.orchestrator_id} is now listening for results and votes...")
        self.channel.start_consuming()


    def close_connection(self):
        """Closes the RabbitMQ connection."""
        self.connection.close()
        print("Orchestrator RabbitMQ connection closed.")

# Example Usage (for testing the framework)
if __name__ == "__main__":
    orchestrator = Orchestrator()
    print("Orchestrator initialized. Ensure RabbitMQ is running and agents are spawned.")
    
    # Sample Code Diff
    sample_code_diff = """
--- a/example.py
+++ b/example.py
@@ -1,4 +1,4 @@
 def add(a, b):
-    return a - b  # Bug: Should be addition
+    return a + b  # Fix: Changed to addition

 def subtract(a, b):
     return a - b
"""

    # --- Orchestration Workflow Example ---
    try:
        # 1. Spawn agents
        security_agent_id = str(uuid.uuid4())
        security_agent = SecurityAgent(security_agent_id)
        
        performance_agent_id = str(uuid.uuid4())
        performance_agent = PerformanceAgent(performance_agent_id)

        # Register agents with orchestrator
        # In a real system, agents would run in separate processes/threads and register themselves
        orchestrator.spawn_agent(security_agent_id, "security")
        orchestrator.spawn_agent(performance_agent_id, "performance")

        # Start agents listening in separate threads
        security_thread = threading.Thread(target=security_agent.start_consuming_tasks)
        performance_thread = threading.Thread(target=performance_agent.start_consuming_tasks)
        security_thread.start()
        performance_thread.start()
        
        time.sleep(2) # Give agents time to start consuming

        # 2. Assign tasks
        security_task_id = orchestrator.assign_task(
            security_agent_id, 
            {"code_diff": sample_code_diff}, 
            task_type="review_code"
        )
        performance_task_id = orchestrator.assign_task(
            performance_agent_id, 
            {"code_diff": sample_code_diff}, 
            task_type="review_code"
        )

        time.sleep(5) # Give agents time to process tasks and send results

        # 3. Collect results (orchestrator's consume_messages callback handles this)
        # For demonstration, we'll manually check task status
        print("\n--- Task Results ---")
        print(f"Security Task {security_task_id} status: {orchestrator.tasks.get(security_task_id)}")
        print(f"Performance Task {performance_task_id} status: {orchestrator.tasks.get(performance_task_id)}")

        # 4. Initiate a vote on a recommendation (e.g., whether to approve a fix)
        vote_topic = "approve_code_fix"
        options = ["Approve", "Reject", "Needs More Info"]
        orchestrator.initiate_vote(security_task_id, vote_topic, options) # Using security task_id for context

        time.sleep(5) # Give agents time to receive vote request and cast votes
        
        # In a real scenario, agents would dynamically receive the VOTE_REQUEST and call agent.send_vote()
        # For this example, we'll manually simulate agents casting votes
        print("\n--- Simulating Agent Votes ---")
        # Security agent votes "Approve"
        security_agent_ch = security_agent.connection.channel()
        security_agent.send_vote(security_agent_ch, security_task_id, "Approve", vote_topic)
        security_agent_ch.close()

        # Performance agent votes "Needs More Info"
        performance_agent_ch = performance_agent.connection.channel()
        performance_agent.send_vote(performance_agent_ch, performance_task_id, "Needs More Info", vote_topic)
        performance_agent_ch.close()


        time.sleep(5) # Give orchestrator time to collect votes

        # 5. Coordinate consensus
        consensus = orchestrator.coordinate_consensus(vote_topic, security_task_id)
        print("\n--- Consensus Result ---")
        print(json.dumps(consensus, indent=2))

    except KeyboardInterrupt:
        print("\nOrchestration workflow stopped by user.")
    finally:
        # Close connections and stop listening thread
        security_agent.close_connection()
        performance_agent.close_connection()
        orchestrator.close_connection()
        print("All connections closed.")