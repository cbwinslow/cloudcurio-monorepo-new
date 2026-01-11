import json
import pika
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import os

# --- Configuration Constants ---
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost") # Use environment variable for host
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# Exchange names
TASK_EXCHANGE = "task_exchange"
RESULT_EXCHANGE = "result_exchange"
VOTE_EXCHANGE = "vote_exchange"
BROADCAST_EXCHANGE = "broadcast_exchange"

# --- Message Structure ---
@dataclass
class AgentMessage:
    """Standard message format for agent communication."""
    sender_id: str
    receiver_id: Optional[str] = None # None for broadcast
    message_type: str # e.g., "TASK", "RESULT", "VOTE", "BROADCAST"
    payload: Dict[str, Any] # Actual data for the message
    task_id: Optional[str] = None # Optional ID to link messages to a task

    def to_json(self) -> str:
        """Converts the message to a JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str):
        """Creates an AgentMessage from a JSON string."""
        return cls(**json.loads(json_str))

# --- RabbitMQ Helper Functions ---
def get_rabbitmq_connection():
    """Establishes and returns a Pika blocking connection."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def declare_exchanges(channel):
    """Declar
es necessary exchanges."""
    channel.exchange_declare(exchange=TASK_EXCHANGE, exchange_type='direct', durable=True)
    channel.exchange_declare(exchange=RESULT_EXCHANGE, exchange_type='direct', durable=True)
    channel.exchange_declare(exchange=VOTE_EXCHANGE, exchange_type='topic', durable=True)
    channel.exchange_declare(exchange=BROADCAST_EXCHANGE, exchange_type='fanout', durable=True)

def send_message(
    channel,
    message: AgentMessage,
    exchange: str,
    routing_key: str = ""
):
    """Sends an AgentMessage to a specified exchange."""
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=message.to_json(),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    print(f" [x] Sent '{message.message_type}' to exchange '{exchange}' with routing key '{routing_key}'")

def consume_messages(queue_name: str, callback):
    """Consumes messages from a specific queue."""
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)
    print(f' [*] Waiting for messages in queue {queue_name}. To exit press CTRL+C')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    channel.start_consuming()
