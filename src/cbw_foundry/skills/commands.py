#!/usr/bin/env python3
"""Slash Command Parser for CloudCurio.

Parses and executes slash commands for skills.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import re
import logging
from .skills import get_registry

logger = logging.getLogger(__name__)


class CommandParser:
    """Parse slash commands."""
    
    # Command pattern: /command param1=value1 param2="value with spaces"
    COMMAND_PATTERN = r'^/(\w+)(?:\s+(.+))?$'
    PARAM_PATTERN = r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\S+))'
    
    def parse(self, command_str: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Parse slash command string.
        
        Args:
            command_str: Command string to parse
        
        Returns:
            Tuple of (command, parameters)
        
        Example:
            >>> parser = CommandParser()
            >>> cmd, params = parser.parse('/search query="AI agents" limit=10')
            >>> print(cmd)  # "search"
            >>> print(params)  # {"query": "AI agents", "limit": "10"}
        """
        # Match command pattern
        match = re.match(self.COMMAND_PATTERN, command_str.strip())
        if not match:
            return None, {}
        
        command = match.group(1)
        params_str = match.group(2)
        
        # Parse parameters
        params = {}
        if params_str:
            params = self._parse_parameters(params_str)
        
        return f"/{command}", params
    
    def _parse_parameters(self, params_str: str) -> Dict[str, Any]:
        """Parse parameter string.
        
        Args:
            params_str: Parameter string
        
        Returns:
            Dictionary of parameters
        """
        params = {}
        
        for match in re.finditer(self.PARAM_PATTERN, params_str):
            key = match.group(1)
            # Get value from whichever group matched (double quote, single quote, or unquoted)
            value = match.group(2) or match.group(3) or match.group(4)
            
            # Type conversion
            value = self._convert_value(value)
            params[key] = value
        
        return params
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type.
        
        Args:
            value: String value
        
        Returns:
            Converted value
        """
        # Boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float
        try:
            return float(value)
        except ValueError:
            pass
        
        # String
        return value


class CommandExecutor:
    """Execute slash commands."""
    
    def __init__(self):
        """Initialize command executor."""
        self.parser = CommandParser()
        self.registry = get_registry()
    
    def execute(self, command_str: str) -> Dict[str, Any]:
        """Execute a slash command.
        
        Args:
            command_str: Command string to execute
        
        Returns:
            Execution result
        
        Example:
            >>> executor = CommandExecutor()
            >>> result = executor.execute('/search query="Python" limit=5')
            >>> print(result["status"])
        """
        # Parse command
        command, params = self.parser.parse(command_str)
        
        if not command:
            return {
                "status": "error",
                "error": "Invalid command format"
            }
        
        logger.info(f"Executing command: {command} with params: {params}")
        
        # Execute via registry
        result = self.registry.execute(command, params)
        
        return result
    
    def help(self, command: Optional[str] = None) -> str:
        """Get help for commands.
        
        Args:
            command: Specific command to get help for, or None for all
        
        Returns:
            Help text
        """
        if command:
            skill = self.registry.get(command)
            if not skill:
                return f"Command not found: {command}"
            
            return self._format_skill_help(skill)
        else:
            skills = self.registry.list_skills()
            if not skills:
                return "No skills registered"
            
            help_text = "Available Commands:\n\n"
            for skill in sorted(skills, key=lambda s: s.command):
                help_text += f"{skill.command} - {skill.description}\n"
            
            help_text += "\nUse /help <command> for detailed information"
            return help_text
    
    def _format_skill_help(self, skill) -> str:
        """Format detailed help for a skill.
        
        Args:
            skill: Skill to format help for
        
        Returns:
            Formatted help text
        """
        help_text = f"Command: {skill.command}\n"
        help_text += f"Description: {skill.description}\n\n"
        
        if skill.parameters:
            help_text += "Parameters:\n"
            for param in skill.parameters:
                required = "required" if param.required else "optional"
                default = f" (default: {param.default})" if param.default is not None else ""
                help_text += f"  {param.name} ({param.type}, {required}){default}\n"
                help_text += f"    {param.description}\n"
        
        if skill.examples:
            help_text += "\nExamples:\n"
            for example in skill.examples:
                help_text += f"  {example.get('command', '')}\n"
                if 'description' in example:
                    help_text += f"    {example['description']}\n"
        
        return help_text


# Global executor instance
_executor = CommandExecutor()


def execute_command(command_str: str) -> Dict[str, Any]:
    """Execute a slash command.
    
    Args:
        command_str: Command string
    
    Returns:
        Execution result
    """
    return _executor.execute(command_str)


def get_help(command: Optional[str] = None) -> str:
    """Get command help.
    
    Args:
        command: Specific command or None for all
    
    Returns:
        Help text
    """
    return _executor.help(command)


__all__ = [
    "CommandParser",
    "CommandExecutor",
    "execute_command",
    "get_help",
]
