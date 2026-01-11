"""Enhanced Base Agent - Comprehensive foundation with all modern AI frameworks.

This module provides an enhanced base agent class that integrates:
- LangChain for advanced LLM capabilities
- OpenTelemetry for observability and tracing
- LangFuse for analytics and monitoring
- CrewAI for multi-agent collaboration
- LangGraph for workflow orchestration
- RobustTool framework for tool execution
- Democratic decision making
- Comprehensive error handling and recovery
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Import all the modern AI frameworks
try:
    # LangChain imports
    from langchain_community.chat_models import ChatOpenAI
    from langchain_community.embeddings import SentenceTransformerEmbeddings
    from langchain_community.llms import OpenAI

    # LangChain Community imports
    from langchain_community.tools import BaseTool
    from langchain_community.vectorstores import FAISS
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.documents import Document
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.runnables import Runnable, RunnableConfig, RunnablePassthrough
    from langchain_core.tools import BaseTool as LangChainBaseTool
    from langchain_core.tracers import BaseTracer

    # CrewAI imports
    try:
        from crewai import Agent, Crew, Process, Task
        from crewai_tools import BaseTool as CrewAIBaseTool
        CREWAI_AVAILABLE = True
    except ImportError:
        CREWAI_AVAILABLE = False

    # LangGraph imports
    try:
        from langgraph.graph import Graph
        from langgraph.prebuilt import HumanNode, ToolNode
        LANGRAPH_AVAILABLE = True
    except ImportError:
        LANGRAPH_AVAILABLE = False

    # OpenTelemetry imports
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        OPENTELEMETRY_AVAILABLE = True
    except ImportError:
        OPENTELEMETRY_AVAILABLE = False

    # LangFuse imports
    try:
        from langfuse import Langfuse
        from langfuse.callback import CallbackHandler
        LANGFUSE_AVAILABLE = True
    except ImportError:
        LANGFUSE_AVAILABLE = False

    # Local imports
    from agents.base_agent import AgentTool, BaseAgent, ConfidenceMetrics
    from agents.robust_tool import RobustTool, ToolResult

except ImportError as e:
    logging.warning(f"Failed to import some AI frameworks: {e}")
    logging.warning("Some features may be limited, but core functionality will still work.")

# Enhanced Agent Tool with LangChain integration
class EnhancedAgentTool(AgentTool):
    """Agent tool that integrates with LangChain and other frameworks."""

    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        """Initialize enhanced agent tool.

        Args:
            name: Tool name
            description: Tool description
            config: Optional tool configuration
        """
        super().__init__(name, description, config)
        self.langchain_tool = None
        self.crewai_tool = None
        self.langgraph_node = None

    def create_langchain_tool(self, func: Callable, return_direct: bool = False) -> LangChainBaseTool:
        """Create a LangChain tool from a function.

        Args:
            func: Function to wrap as a tool
            return_direct: Whether to return tool output directly

        Returns:
            LangChain tool instance
        """
        from langchain_core.tools import tool

        @tool
        def langchain_tool_wrapper(*args, **kwargs):
            """LangChain tool wrapper."""
            return func(*args, **kwargs)

        self.langchain_tool = langchain_tool_wrapper
        return self.langchain_tool

    def create_crewai_tool(self, func: Callable) -> Optional[CrewAIBaseTool]:
        """Create a CrewAI tool from a function.

        Args:
            func: Function to wrap as a tool

        Returns:
            CrewAI tool instance or None if CrewAI not available
        """
        if not CREWAI_AVAILABLE:
            return None

        crewai_tool = CrewAIBaseTool(
            name=self.name,
            description=self.description,
            func=func
        )
        self.crewai_tool = crewai_tool
        return crewai_tool

    def create_langgraph_node(self) -> Optional[ToolNode]:
        """Create a LangGraph node from this tool.

        Returns:
            LangGraph ToolNode or None if LangGraph not available
        """
        if not LANGRAPH_AVAILABLE or not self.langchain_tool:
            return None

        node = ToolNode([self.langchain_tool])
        self.langgraph_node = node
        return node

# Enhanced Base Agent with all frameworks
class EnhancedBaseAgent(BaseAgent):
    """Enhanced base agent with all modern AI frameworks integrated."""

    def __init__(self, agent_name: str, config_path: Optional[str] = None):
        """Initialize the enhanced agent.

        Args:
            agent_name: Name of the agent (must match agents_config.json)
            config_path: Optional path to agents_config.json
        """
        super().__init__(agent_name, config_path)

        # Initialize framework integrations
        self.langchain_agent = None
        self.crewai_agent = None
        self.langgraph_workflow = None
        self.telemetry_tracer = None
        self.langfuse_handler = None

        # Initialize framework availability
        self.frameworks_available = {
            'langchain': True,
            'crewai': CREWAI_AVAILABLE,
            'langgraph': LANGRAPH_AVAILABLE,
            'opentelemetry': OPENTELEMETRY_AVAILABLE,
            'langfuse': LANGFUSE_AVAILABLE
        }

        # Initialize observability
        self._initialize_observability()

        # Initialize LangChain agent
        self._initialize_langchain_agent()

        # Initialize CrewAI agent
        self._initialize_crewai_agent()

        # Initialize LangGraph workflow
        self._initialize_langgraph_workflow()

        self.logger.info(f"Initialized enhanced agent '{self.name}' with frameworks: {self.frameworks_available}")

    def _initialize_observability(self) -> None:
        """Initialize OpenTelemetry and LangFuse for observability."""
        # Initialize OpenTelemetry
        if OPENTELEMETRY_AVAILABLE:
            try:
                trace.set_tracer_provider(TracerProvider())
                otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
                span_processor = BatchSpanProcessor(otlp_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
                self.telemetry_tracer = trace.get_tracer(__name__)
                self.logger.info("OpenTelemetry tracing initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenTelemetry: {e}")
                self.frameworks_available['opentelemetry'] = False

        # Initialize LangFuse
        if LANGFUSE_AVAILABLE:
            try:
                self.langfuse_handler = CallbackHandler(
                    public_key="your-public-key",
                    secret_key="your-secret-key",
                    host="https://cloud.langfuse.com"
                )
                self.logger.info("LangFuse analytics initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize LangFuse: {e}")
                self.frameworks_available['langfuse'] = False

    def _initialize_langchain_agent(self) -> None:
        """Initialize LangChain agent with tools."""
        try:
            # Create LangChain tools from our agent tools
            langchain_tools = []
            for tool_name, agent_tool in self.tools.items():
                if isinstance(agent_tool, EnhancedAgentTool):
                    langchain_tool = agent_tool.create_langchain_tool(agent_tool.execute)
                    if langchain_tool:
                        langchain_tools.append(langchain_tool)

            # Create LangChain prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessage(content="{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # Create LangChain agent
            from langchain.agents import create_openai_functions_agent
            from langchain.agents.agent import AgentExecutor

            llm = ChatOpenAI(model=self.model, temperature=0)

            # Create the agent
            agent = create_openai_functions_agent(
                llm=llm,
                tools=langchain_tools,
                prompt=prompt
            )

            # Create agent executor
            self.langchain_agent = AgentExecutor(
                agent=agent,
                tools=langchain_tools,
                verbose=True,
                handle_parsing_errors=True,
                callbacks=[self.langfuse_handler] if self.langfuse_handler else None
            )

            self.logger.info(f"LangChain agent initialized with {len(langchain_tools)} tools")

        except Exception as e:
            self.logger.error(f"Failed to initialize LangChain agent: {e}")
            self.frameworks_available['langchain'] = False

    def _initialize_crewai_agent(self) -> None:
        """Initialize CrewAI agent."""
        if not CREWAI_AVAILABLE:
            return

        try:
            # Create CrewAI tools from our agent tools
            crewai_tools = []
            for tool_name, agent_tool in self.tools.items():
                if isinstance(agent_tool, EnhancedAgentTool):
                    crewai_tool = agent_tool.create_crewai_tool(agent_tool.execute)
                    if crewai_tool:
                        crewai_tools.append(crewai_tool)

            # Create CrewAI agent
            self.crewai_agent = Agent(
                role=self.role,
                goal=self.system_prompt,
                backstory=f"AI agent specialized in {self.role}",
                tools=crewai_tools,
                verbose=True,
                allow_delegation=True
            )

            self.logger.info(f"CrewAI agent initialized with {len(crewai_tools)} tools")

        except Exception as e:
            self.logger.error(f"Failed to initialize CrewAI agent: {e}")
            self.frameworks_available['crewai'] = False

    def _initialize_langgraph_workflow(self) -> None:
        """Initialize LangGraph workflow."""
        if not LANGRAPH_AVAILABLE:
            return

        try:
            # Create LangGraph nodes from our tools
            tool_nodes = {}
            for tool_name, agent_tool in self.tools.items():
                if isinstance(agent_tool, EnhancedAgentTool):
                    node = agent_tool.create_langgraph_node()
                    if node:
                        tool_nodes[tool_name] = node

            # Create workflow graph
            workflow = Graph()

            # Add tool nodes
            for node_name, node in tool_nodes.items():
                workflow.add_node(node_name, node)

            # Add human node for interaction
            workflow.add_node("human", HumanNode())

            # Connect nodes (simple linear workflow for now)
            last_node = "human"
            for node_name in tool_nodes.keys():
                workflow.add_edge(last_node, node_name)
                last_node = node_name

            # Set entry point
            workflow.set_entry_point("human")

            # Compile workflow
            self.langgraph_workflow = workflow.compile()

            self.logger.info(f"LangGraph workflow initialized with {len(tool_nodes)} tool nodes")

        except Exception as e:
            self.logger.error(f"Failed to initialize LangGraph workflow: {e}")
            self.frameworks_available['langgraph'] = False

    def execute_with_langchain(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task using LangChain agent.

        Args:
            task: Task description
            context: Optional context for the task

        Returns:
            Dictionary with execution results
        """
        if not self.frameworks_available['langchain'] or not self.langchain_agent:
            return {"error": "LangChain not available", "success": False}

        try:
            # Start observability span
            if self.telemetry_tracer:
                with self.telemetry_tracer.start_as_current_span(f"{self.name}_langchain_execution"):
                    result = self.langchain_agent.invoke({
                        "input": task,
                        "chat_history": context.get("chat_history", []) if context else []
                    })

            # Update confidence metrics
            success = result.get("output", "").strip() != ""
            self.update_confidence_after_execution("langchain_execution", success)

            return {
                "success": success,
                "result": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "framework": "langchain"
            }

        except Exception as e:
            self.logger.error(f"LangChain execution failed: {e}")
            self.update_confidence_after_execution("langchain_execution", False)
            return {"error": str(e), "success": False, "framework": "langchain"}

    def execute_with_crewai(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task using CrewAI agent.

        Args:
            task: Task description
            context: Optional context for the task

        Returns:
            Dictionary with execution results
        """
        if not self.frameworks_available['crewai'] or not self.crewai_agent:
            return {"error": "CrewAI not available", "success": False}

        try:
            # Create CrewAI task
            crewai_task = Task(
                description=task,
                agent=self.crewai_agent,
                expected_output="Detailed response to the task",
                context=context or {}
            )

            # Create and execute crew
            crew = Crew(
                agents=[self.crewai_agent],
                tasks=[crewai_task],
                process=Process.sequential,
                verbose=True
            )

            # Start observability span
            if self.telemetry_tracer:
                with self.telemetry_tracer.start_as_current_span(f"{self.name}_crewai_execution"):
                    result = crew.kickoff()

            # Update confidence metrics
            success = result.strip() != ""
            self.update_confidence_after_execution("crewai_execution", success)

            return {
                "success": success,
                "result": result,
                "framework": "crewai"
            }

        except Exception as e:
            self.logger.error(f"CrewAI execution failed: {e}")
            self.update_confidence_after_execution("crewai_execution", False)
            return {"error": str(e), "success": False, "framework": "crewai"}

    async def execute_with_langgraph(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task using LangGraph workflow.

        Args:
            task: Task description
            context: Optional context for the task

        Returns:
            Dictionary with execution results
        """
        if not self.frameworks_available['langgraph'] or not self.langgraph_workflow:
            return {"error": "LangGraph not available", "success": False}

        try:
            # Start observability span
            if self.telemetry_tracer:
                with self.telemetry_tracer.start_as_current_span(f"{self.name}_langgraph_execution"):
                    # Execute workflow
                    result = await self.langgraph_workflow.ainvoke({
                        "messages": [HumanMessage(content=task)],
                        "context": context or {}
                    })

            # Update confidence metrics
            success = result.get("messages", [{}])[-1].get("content", "").strip() != ""
            self.update_confidence_after_execution("langgraph_execution", success)

            return {
                "success": success,
                "result": result.get("messages", [{}])[-1].get("content", ""),
                "framework": "langgraph"
            }

        except Exception as e:
            self.logger.error(f"LangGraph execution failed: {e}")
            self.update_confidence_after_execution("langgraph_execution", False)
            return {"error": str(e), "success": False, "framework": "langgraph"}

    def execute_task(self, task: str, framework: str = "auto", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a task using the specified framework.

        Args:
            task: Task description
            framework: Framework to use ('auto', 'langchain', 'crewai', 'langgraph')
            context: Optional context for the task

        Returns:
            Dictionary with execution results
        """
        framework = framework.lower()

        # Auto-select framework based on availability and confidence
        if framework == "auto":
            # Try frameworks in order of preference
            if self.frameworks_available['langgraph']:
                return self.execute_with_langgraph(task, context)
            elif self.frameworks_available['crewai']:
                return self.execute_with_crewai(task, context)
            elif self.frameworks_available['langchain']:
                return self.execute_with_langchain(task, context)
            else:
                return {"error": "No AI frameworks available", "success": False}

        # Execute with specified framework
        if framework == "langchain":
            return self.execute_with_langchain(task, context)
        elif framework == "crewai":
            return self.execute_with_crewai(task, context)
        elif framework == "langgraph":
            return asyncio.run(self.execute_with_langgraph(task, context))
        else:
            return {"error": f"Unknown framework: {framework}", "success": False}

    def get_available_frameworks(self) -> Dict[str, bool]:
        """Get availability status of all frameworks.

        Returns:
            Dictionary with framework availability
        """
        return self.frameworks_available.copy()

    def get_framework_status(self) -> Dict[str, Any]:
        """Get detailed status of all framework integrations.

        Returns:
            Dictionary with framework status information
        """
        status = {
            "agent_name": self.name,
            "frameworks": self.frameworks_available.copy(),
            "langchain_agent": bool(self.langchain_agent),
            "crewai_agent": bool(self.crewai_agent),
            "langgraph_workflow": bool(self.langgraph_workflow),
            "observability": {
                "opentelemetry": bool(self.telemetry_tracer),
                "langfuse": bool(self.langfuse_handler)
            }
        }
        return status

    def enhanced_execute_tool(self, tool_name: str, parameters: Dict[str, Any],
                            framework: str = "auto") -> Dict[str, Any]:
        """Execute a tool using enhanced framework capabilities.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            framework: Framework to use for execution

        Returns:
            Dictionary with execution results
        """
        # First execute with base agent
        base_result = super().execute_tool(tool_name, parameters)

        # Enhance with framework capabilities
        if framework == "auto":
            # Use the most appropriate framework based on tool type
            if "search" in tool_name.lower() or "retrieve" in tool_name.lower():
                framework = "langchain"
            elif "collaborate" in tool_name.lower() or "team" in tool_name.lower():
                framework = "crewai"
            else:
                framework = "langgraph"

        # Execute with selected framework
        framework_result = self.execute_task(
            f"Execute tool {tool_name} with parameters {parameters}",
            framework=framework,
            context={"tool_result": base_result.to_dict()}
        )

        # Combine results
        return {
            "base_result": base_result.to_dict(),
            "framework_result": framework_result,
            "success": base_result.success and framework_result.get("success", False),
            "framework_used": framework
        }

    def create_enhanced_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an enhanced workflow using all available frameworks.

        Args:
            workflow_name: Name of the workflow
            steps: List of workflow steps

        Returns:
            Dictionary with workflow creation results
        """
        workflow = {
            "name": workflow_name,
            "steps": steps,
            "frameworks_used": [],
            "creation_time": time.time(),
            "status": "created"
        }

        # Create LangChain workflow
        if self.frameworks_available['langchain']:
            try:
                from langchain.chains import LLMChain
                from langchain.prompts import PromptTemplate

                # Create workflow chain
                prompt = PromptTemplate.from_template(
                    "Execute workflow {workflow_name} with steps: {steps}"
                )
                chain = LLMChain(llm=ChatOpenAI(model=self.model), prompt=prompt)
                workflow["langchain_chain"] = chain
                workflow["frameworks_used"].append("langchain")

            except Exception as e:
                self.logger.error(f"Failed to create LangChain workflow: {e}")

        # Create CrewAI workflow
        if self.frameworks_available['crewai']:
            try:
                crewai_tasks = []
                for i, step in enumerate(steps):
                    task = Task(
                        description=step.get("description", f"Step {i+1}"),
                        agent=self.crewai_agent,
                        expected_output=step.get("expected_output", "Step completion")
                    )
                    crewai_tasks.append(task)

                workflow["crewai_tasks"] = crewai_tasks
                workflow["frameworks_used"].append("crewai")

            except Exception as e:
                self.logger.error(f"Failed to create CrewAI workflow: {e}")

        # Create LangGraph workflow
        if self.frameworks_available['langgraph']:
            try:
                graph = Graph()

                # Add nodes for each step
                for i, step in enumerate(steps):
                    node_name = f"step_{i+1}"

                    # Define the tool function
                    def create_step_tool(step_num: int):
                        def step_tool(step_desc: str) -> str:
                            """Execute workflow step."""
                            return f"Executed step {step_num}: {step_desc}"
                        return step_tool

                    step_tool_func = create_step_tool(i+1)

                    # Create LangChain tool
                    from langchain_core.tools import tool
                    step_tool_lc = tool(step_tool_func)

                    graph.add_node(node_name, ToolNode([step_tool_lc]))

                    # Connect nodes
                    if i > 0:
                        graph.add_edge(f"step_{i}", node_name)

                # Set entry point
                if steps:
                    graph.set_entry_point("step_1")

                workflow["langgraph_workflow"] = graph.compile()
                workflow["frameworks_used"].append("langgraph")

            except Exception as e:
                self.logger.error(f"Failed to create LangGraph workflow: {e}")

        workflow["status"] = "ready" if workflow["frameworks_used"] else "failed"
        return workflow

    def execute_enhanced_workflow(self, workflow: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an enhanced workflow created with create_enhanced_workflow.

        Args:
            workflow: Workflow definition
            inputs: Input parameters

        Returns:
            Dictionary with workflow execution results
        """
        results = {
            "workflow_name": workflow["name"],
            "framework_results": {},
            "success": True,
            "errors": []
        }

        # Execute with each framework that was used to create the workflow
        for framework in workflow.get("frameworks_used", []):
            try:
                if framework == "langchain" and "langchain_chain" in workflow:
                    langchain_result = workflow["langchain_chain"].run({
                        "workflow_name": workflow["name"],
                        "steps": str(workflow["steps"])
                    })
                    results["framework_results"]["langchain"] = {
                        "success": True,
                        "result": langchain_result
                    }

                elif framework == "crewai" and "crewai_tasks" in workflow:
                    crew = Crew(
                        agents=[self.crewai_agent],
                        tasks=workflow["crewai_tasks"],
                        process=Process.sequential
                    )
                    crewai_result = crew.kickoff()
                    results["framework_results"]["crewai"] = {
                        "success": True,
                        "result": crewai_result
                    }

                elif framework == "langgraph" and "langgraph_workflow" in workflow:
                    langgraph_result = asyncio.run(workflow["langgraph_workflow"].ainvoke({
                        "messages": [HumanMessage(content=f"Execute workflow {workflow['name']}")]
                    }))
                    results["framework_results"]["langgraph"] = {
                        "success": True,
                        "result": langgraph_result
                    }

            except Exception as e:
                results["framework_results"][framework] = {
                    "success": False,
                    "error": str(e)
                }
                results["success"] = False
                results["errors"].append(f"{framework}: {str(e)}")

        return results

    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the enhanced agent.

        Returns:
            Dictionary with enhanced agent status
        """
        base_status = self.get_status()
        framework_status = self.get_framework_status()

        return {
            **base_status,
            **framework_status,
            "enhanced_capabilities": {
                "multi_framework_execution": True,
                "observability_integration": any([self.telemetry_tracer, self.langfuse_handler]),
                "workflow_orchestration": any([
                    self.frameworks_available['langchain'],
                    self.frameworks_available['crewai'],
                    self.frameworks_available['langgraph']
                ]),
                "democratic_decision_making": True,
                "confidence_tracking": True
            }
        }

# Enhanced Tool-Based Agent
class EnhancedToolBasedAgent(EnhancedBaseAgent):
    """Enhanced agent that uses framework-integrated tools."""

    def _initialize_tools(self) -> Dict[str, AgentTool]:
        """Initialize enhanced tools from agent configuration."""
        tools = {}

        # Get tool configurations from agent config
        tool_configs = self.agent_config.get("tools", [])

        for tool_config in tool_configs:
            tool_name = tool_config["name"]
            tool_description = tool_config["description"]
            tool_params_config = tool_config.get("parameters", {})

            # Create enhanced agent tool wrapper
            enhanced_tool = EnhancedAgentTool(
                name=tool_name,
                description=tool_description,
                config=tool_params_config
            )

            # Create LangChain tool
            enhanced_tool.create_langchain_tool(enhanced_tool.execute)

            # Create CrewAI tool if available
            if CREWAI_AVAILABLE:
                enhanced_tool.create_crewai_tool(enhanced_tool.execute)

            # Create LangGraph node if available
            if LANGRAPH_AVAILABLE:
                enhanced_tool.create_langgraph_node()

            tools[tool_name] = enhanced_tool

        return tools

# Enhanced Workflow Orchestrator
class EnhancedWorkflowOrchestrator:
    """Orchestrates multi-agent workflows with all framework integrations."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize enhanced workflow orchestrator.

        Args:
            config_path: Optional path to agents_config.json
        """
        self.config_path = config_path or "agents_config.json"
        self.config = self._load_config()
        self.agents: Dict[str, EnhancedBaseAgent] = {}
        self.workflows = self.config.get("workflows", {})

        # Initialize framework integrations
        self.telemetry_tracer = None
        self.langfuse_handler = None
        self._initialize_observability()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from agents_config.json."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(config_file, 'r') as f:
            return json.load(f)

    def _initialize_observability(self) -> None:
        """Initialize observability for the orchestrator."""
        if OPENTELEMETRY_AVAILABLE:
            try:
                trace.set_tracer_provider(TracerProvider())
                otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
                span_processor = BatchSpanProcessor(otlp_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
                self.telemetry_tracer = trace.get_tracer(__name__)
            except Exception as e:
                logging.error(f"Failed to initialize OpenTelemetry for orchestrator: {e}")

        if LANGFUSE_AVAILABLE:
            try:
                self.langfuse_handler = CallbackHandler(
                    public_key="your-public-key",
                    secret_key="your-secret-key",
                    host="https://cloud.langfuse.com"
                )
            except Exception as e:
                logging.error(f"Failed to initialize LangFuse for orchestrator: {e}")

    def get_enhanced_agent(self, agent_name: str) -> EnhancedBaseAgent:
        """Get or create an enhanced agent instance.

        Args:
            agent_name: Name of the agent

        Returns:
            Enhanced agent instance
        """
        if agent_name not in self.agents:
            self.agents[agent_name] = EnhancedToolBasedAgent(agent_name, self.config_path)

        return self.agents[agent_name]

    def execute_enhanced_workflow(self, workflow_name: str, inputs: Dict[str, Any],
                                framework: str = "auto") -> Dict[str, Any]:
        """Execute a multi-agent workflow with enhanced framework capabilities.

        Args:
            workflow_name: Name of the workflow
            inputs: Workflow input parameters
            framework: Framework to use for execution

        Returns:
            Workflow execution results
        """
        if workflow_name not in self.workflows:
            return {"error": f"Workflow {workflow_name} not found", "success": False}

        workflow_config = self.workflows[workflow_name]
        workflow_agents = workflow_config.get("agents", [])
        workflow_steps = workflow_config.get("steps", [])

        # Start observability span
        if self.telemetry_tracer:
            with self.telemetry_tracer.start_as_current_span(f"workflow_{workflow_name}_execution"):
                return self._execute_workflow_steps(workflow_name, workflow_steps, inputs, framework)
        else:
            return self._execute_workflow_steps(workflow_name, workflow_steps, inputs, framework)

    def _execute_workflow_steps(self, workflow_name: str, steps: List[Dict[str, Any]],
                              inputs: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Execute workflow steps with the specified framework.

        Args:
            workflow_name: Name of the workflow
            steps: Workflow steps
            inputs: Input parameters
            framework: Framework to use

        Returns:
            Workflow execution results
        """
        results = {}
        current_context = inputs.copy()

        for step in steps:
            agent_name = step["agent"]
            action = step["action"]
            step_input = step.get("input", "")

            # Get the agent
            agent = self.get_enhanced_agent(agent_name)

            # Prepare step inputs
            step_parameters = self._resolve_step_inputs(step_input, current_context, results)

            # Execute the action with the specified framework
            step_result = agent.execute_task(
                f"Execute action {action} with parameters {step_parameters}",
                framework=framework,
                context={"step": step, "workflow": workflow_name}
            )

            # Store result
            step_key = f"{agent_name}.{action}"
            results[step_key] = step_result

            # Update context for next steps
            if step_result.get("success"):
                current_context[step_key] = step_result

            # Stop on failure
            if not step_result.get("success"):
                logging.error(f"Workflow {workflow_name} failed at step {step_key}")
                break

        workflow_success = all(r.get("success", False) for r in results.values())

        return {
            "workflow": workflow_name,
            "success": workflow_success,
            "steps_executed": len(results),
            "results": results,
            "inputs": inputs,
            "framework_used": framework
        }

    def _resolve_step_inputs(self, input_spec: str, context: Dict[str, Any],
                           results: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve step inputs from specification.

        Args:
            input_spec: Input specification string
            context: Current workflow context
            results: Previous step results

        Returns:
            Resolved input parameters
        """
        if not input_spec:
            return context

        # Simple key resolution
        if input_spec in context:
            return context[input_spec]

        # Check results
        if input_spec in results:
            return results[input_spec].get("result", {})

        # Default to entire context
        return context

    def create_multi_framework_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a workflow that can be executed with multiple frameworks.

        Args:
            workflow_name: Name of the workflow
            steps: List of workflow steps

        Returns:
            Dictionary with workflow creation results
        """
        workflow = {
            "name": workflow_name,
            "steps": steps,
            "frameworks": {
                "langchain": None,
                "crewai": None,
                "langgraph": None
            },
            "creation_time": time.time()
        }

        # Create LangChain version
        if LANGRAPH_AVAILABLE:
            try:
                from langchain.chains import LLMChain
                from langchain.prompts import PromptTemplate

                prompt = PromptTemplate.from_template(
                    "Execute multi-framework workflow {workflow_name} with steps: {steps}"
                )
                chain = LLMChain(llm=ChatOpenAI(model="gpt-4o"), prompt=prompt)
                workflow["frameworks"]["langchain"] = chain

            except Exception as e:
                logging.error(f"Failed to create LangChain workflow: {e}")

        # Create CrewAI version
        if CREWAI_AVAILABLE:
            try:
                crewai_tasks = []
                for i, step in enumerate(steps):
                    task = Task(
                        description=step.get("description", f"Step {i+1}"),
                        expected_output=step.get("expected_output", "Step completion")
                    )
                    crewai_tasks.append(task)

                workflow["frameworks"]["crewai"] = {
                    "tasks": crewai_tasks,
                    "process": Process.sequential
                }

            except Exception as e:
                logging.error(f"Failed to create CrewAI workflow: {e}")

        # Create LangGraph version
        if LANGRAPH_AVAILABLE:
            try:
                graph = Graph()

                # Add nodes for each step
                for i, step in enumerate(steps):
                    node_name = f"step_{i+1}"

                    # Define the tool function
                    def create_step_tool(step_num: int):
                        def step_tool(step_desc: str) -> str:
                            """Execute workflow step."""
                            return f"Executed step {step_num}: {step_desc}"
                        return step_tool

                    step_tool_func = create_step_tool(i+1)

                    # Create LangChain tool
                    from langchain_core.tools import tool
                    step_tool_lc = tool(step_tool_func)

                    graph.add_node(node_name, ToolNode([step_tool_lc]))

                    # Connect nodes
                    if i > 0:
                        graph.add_edge(f"step_{i}", node_name)

                # Set entry point
                if steps:
                    graph.set_entry_point("step_1")

                workflow["frameworks"]["langgraph"] = graph.compile()

            except Exception as e:
                logging.error(f"Failed to create LangGraph workflow: {e}")

        return workflow

    def get_available_frameworks(self) -> Dict[str, bool]:
        """Get availability of all frameworks.

        Returns:
            Dictionary with framework availability
        """
        return {
            "langchain": LANGRAPH_AVAILABLE,
            "crewai": CREWAI_AVAILABLE,
            "langgraph": LANGRAPH_AVAILABLE,
            "opentelemetry": OPENTELEMETRY_AVAILABLE,
            "langfuse": LANGFUSE_AVAILABLE
        }
