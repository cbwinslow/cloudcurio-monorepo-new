"""CloudCurio Swarm System - Multi-agent coordination and orchestration.

This module provides the core swarm orchestration system for coordinating
multiple agents to work together on complex tasks.

Key Components:
- Swarm: Main orchestration container
- SwarmAgent: Agent wrapper for swarm participation
- SwarmConfig: Configuration for swarm behavior
- SwarmResult: Result container for swarm executions

Usage:
    from cbw_foundry.swarm import Swarm, SwarmAgent, SwarmConfig
    
    # Create agents
    agents = [
        SwarmAgent(name="generator", role="worker"),
        SwarmAgent(name="reviewer", role="reviewer"),
    ]
    
    # Create swarm
    swarm = Swarm(
        name="content_pipeline",
        agents=agents,
        config=SwarmConfig(coordination_mode="sequential")
    )
    
    # Execute task
    result = swarm.execute({"task": "Generate content"})
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CoordinationMode(str, Enum):
    """Coordination modes for swarm execution."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DEMOCRATIC = "democratic"
    HIERARCHICAL = "hierarchical"


@dataclass
class SwarmConfig:
    """Configuration for swarm behavior."""
    
    coordination_mode: CoordinationMode = CoordinationMode.SEQUENTIAL
    max_iterations: int = 10
    quality_threshold: float = 0.8
    enable_voting: bool = True
    enable_knowledge_sharing: bool = True
    timeout: int = 600  # seconds
    
    def validate(self) -> None:
        """Validate configuration."""
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        if not 0 <= self.quality_threshold <= 1:
            raise ValueError("quality_threshold must be between 0 and 1")
        if self.timeout < 0:
            raise ValueError("timeout must be non-negative")


@dataclass
class SwarmAgent:
    """Agent wrapper for swarm participation."""
    
    name: str
    role: str  # coordinator, worker, reviewer, specialist
    capabilities: List[str] = field(default_factory=list)
    confidence: float = 0.8
    agent_instance: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate agent configuration."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        
        valid_roles = ["coordinator", "worker", "reviewer", "specialist"]
        if self.role not in valid_roles:
            raise ValueError(f"role must be one of {valid_roles}")


@dataclass
class SwarmResult:
    """Result container for swarm execution."""
    
    success: bool
    output: Any
    agent_outputs: Dict[str, Any] = field(default_factory=dict)
    iterations: int = 0
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class Swarm:
    """Multi-agent swarm orchestrator.
    
    Coordinates multiple agents to work together on complex tasks.
    Supports various coordination modes and quality assurance mechanisms.
    """
    
    def __init__(
        self,
        name: str,
        agents: List[SwarmAgent],
        config: Optional[SwarmConfig] = None
    ):
        """Initialize swarm.
        
        Args:
            name: Swarm identifier
            agents: List of agents in the swarm
            config: Swarm configuration
        """
        self.name = name
        self.agents = agents
        self.config = config or SwarmConfig()
        self.config.validate()
        
        # Validate agents
        if not agents:
            raise ValueError("Swarm must have at least one agent")
        
        # Initialize state
        self._iteration = 0
        self._results: Dict[str, Any] = {}
        
        logger.info(
            f"Initialized swarm '{name}' with {len(agents)} agents "
            f"in {self.config.coordination_mode} mode"
        )
    
    def execute(self, task: Dict[str, Any]) -> SwarmResult:
        """Execute task using swarm coordination.
        
        Args:
            task: Task specification
            
        Returns:
            SwarmResult with execution outcome
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Swarm '{self.name}' starting task execution")
            
            # Execute based on coordination mode
            if self.config.coordination_mode == CoordinationMode.SEQUENTIAL:
                output = self._execute_sequential(task)
            elif self.config.coordination_mode == CoordinationMode.PARALLEL:
                output = self._execute_parallel(task)
            elif self.config.coordination_mode == CoordinationMode.DEMOCRATIC:
                output = self._execute_democratic(task)
            elif self.config.coordination_mode == CoordinationMode.HIERARCHICAL:
                output = self._execute_hierarchical(task)
            else:
                raise ValueError(f"Unknown coordination mode: {self.config.coordination_mode}")
            
            execution_time = time.time() - start_time
            
            logger.info(
                f"Swarm '{self.name}' completed in {execution_time:.2f}s "
                f"after {self._iteration} iterations"
            )
            
            return SwarmResult(
                success=True,
                output=output,
                agent_outputs=self._results,
                iterations=self._iteration,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Swarm '{self.name}' failed: {e}", exc_info=True)
            
            return SwarmResult(
                success=False,
                output=None,
                agent_outputs=self._results,
                iterations=self._iteration,
                execution_time=execution_time,
                error=str(e)
            )
    
    def _execute_sequential(self, task: Dict[str, Any]) -> Any:
        """Execute agents sequentially."""
        current_input = task
        
        for agent in self.agents:
            logger.debug(f"Executing agent '{agent.name}' in sequence")
            result = self._execute_agent(agent, current_input)
            self._results[agent.name] = result
            current_input = result  # Pass output to next agent
            self._iteration += 1
        
        return current_input
    
    def _execute_parallel(self, task: Dict[str, Any]) -> Any:
        """Execute agents in parallel."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            futures = {
                executor.submit(self._execute_agent, agent, task): agent
                for agent in self.agents
            }
            
            for future in as_completed(futures):
                agent = futures[future]
                try:
                    result = future.result()
                    results[agent.name] = result
                    self._results[agent.name] = result
                except Exception as e:
                    logger.error(f"Agent '{agent.name}' failed: {e}")
                    results[agent.name] = {"error": str(e)}
        
        self._iteration += 1
        return results
    
    def _execute_democratic(self, task: Dict[str, Any]) -> Any:
        """Execute with democratic voting."""
        # Execute all agents
        proposals = {}
        for agent in self.agents:
            result = self._execute_agent(agent, task)
            proposals[agent.name] = {
                "result": result,
                "confidence": agent.confidence
            }
            self._results[agent.name] = result
        
        # Democratic voting on best result
        best_proposal = max(
            proposals.items(),
            key=lambda x: x[1]["confidence"]
        )
        
        self._iteration += 1
        return best_proposal[1]["result"]
    
    def _execute_hierarchical(self, task: Dict[str, Any]) -> Any:
        """Execute with hierarchical coordination."""
        # Find coordinator
        coordinator = next(
            (a for a in self.agents if a.role == "coordinator"),
            None
        )
        
        if not coordinator:
            raise ValueError("Hierarchical mode requires a coordinator agent")
        
        # Coordinator delegates to workers
        worker_results = {}
        workers = [a for a in self.agents if a.role == "worker"]
        
        for worker in workers:
            result = self._execute_agent(worker, task)
            worker_results[worker.name] = result
            self._results[worker.name] = result
        
        # Coordinator aggregates results
        aggregated_task = {**task, "worker_results": worker_results}
        final_result = self._execute_agent(coordinator, aggregated_task)
        self._results[coordinator.name] = final_result
        
        self._iteration += 1
        return final_result
    
    def _execute_agent(self, agent: SwarmAgent, input_data: Any) -> Any:
        """Execute a single agent.
        
        Args:
            agent: Agent to execute
            input_data: Input for the agent
            
        Returns:
            Agent execution result
        """
        if agent.agent_instance:
            # Use actual agent instance if available
            return agent.agent_instance.execute(input_data)
        else:
            # Placeholder for agents without implementation
            logger.debug(f"Agent '{agent.name}' has no implementation, returning mock result")
            return {
                "agent": agent.name,
                "role": agent.role,
                "input": input_data,
                "status": "mock_execution"
            }
    
    def get_agent(self, name: str) -> Optional[SwarmAgent]:
        """Get agent by name."""
        return next((a for a in self.agents if a.name == name), None)
    
    def add_agent(self, agent: SwarmAgent) -> None:
        """Add agent to swarm."""
        if self.get_agent(agent.name):
            raise ValueError(f"Agent '{agent.name}' already exists in swarm")
        self.agents.append(agent)
        logger.info(f"Added agent '{agent.name}' to swarm '{self.name}'")
    
    def remove_agent(self, name: str) -> bool:
        """Remove agent from swarm."""
        agent = self.get_agent(name)
        if agent:
            self.agents.remove(agent)
            logger.info(f"Removed agent '{name}' from swarm '{self.name}'")
            return True
        return False


__all__ = [
    "Swarm",
    "SwarmAgent",
    "SwarmConfig",
    "SwarmResult",
    "CoordinationMode",
]
