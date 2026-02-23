#!/usr/bin/env python3
"""File System Tools.

Tools for file operations, directory management, and file processing.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileConfig(BaseModel):
    """Configuration for file tools."""
    
    base_path: str = Field(default=".", description="Base directory path")
    allowed_extensions: Optional[List[str]] = Field(
        default=None,
        description="List of allowed file extensions"
    )
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Max file size in bytes")


class FileReaderTool:
    """Read content from files."""
    
    name: str = "file_reader"
    description: str = "Read text content from files"
    
    def __init__(self, config: Optional[FileConfig] = None) -> None:
        """Initialize file reader tool."""
        self.config = config or FileConfig()
    
    def execute(self, filepath: str, encoding: str = "utf-8", **kwargs: Any) -> Dict[str, Any]:
        """Read file content.
        
        Args:
            filepath: Path to file to read
            encoding: File encoding (default: utf-8)
            **kwargs: Additional parameters
        
        Returns:
            File content and metadata
        """
        try:
            path = Path(self.config.base_path) / filepath
            
            if not path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {filepath}",
                    "content": None
                }
            
            if path.stat().st_size > self.config.max_file_size:
                return {
                    "status": "error",
                    "error": f"File too large: {path.stat().st_size} bytes",
                    "content": None
                }
            
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "status": "success",
                "filepath": str(path),
                "content": content,
                "size": path.stat().st_size,
                "lines": len(content.splitlines())
            }
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "filepath": filepath,
                "content": None
            }


class FileWriterTool:
    """Write content to files."""
    
    name: str = "file_writer"
    description: str = "Write text content to files"
    
    def __init__(self, config: Optional[FileConfig] = None) -> None:
        """Initialize file writer tool."""
        self.config = config or FileConfig()
    
    def execute(
        self,
        filepath: str,
        content: str,
        mode: str = "w",
        encoding: str = "utf-8",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Write content to file.
        
        Args:
            filepath: Path to file to write
            content: Content to write
            mode: Write mode ('w' for write, 'a' for append)
            encoding: File encoding (default: utf-8)
            **kwargs: Additional parameters
        
        Returns:
            Write operation result and metadata
        """
        try:
            path = Path(self.config.base_path) / filepath
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
            
            return {
                "status": "success",
                "filepath": str(path),
                "size": path.stat().st_size,
                "mode": mode
            }
        except Exception as e:
            logger.error(f"File write failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "filepath": filepath
            }


class DirectoryTool:
    """Manage directories and list files."""
    
    name: str = "directory_tool"
    description: str = "List, create, and manage directories"
    
    def __init__(self, config: Optional[FileConfig] = None) -> None:
        """Initialize directory tool."""
        self.config = config or FileConfig()
    
    def execute(
        self,
        action: str,
        dirpath: str = ".",
        pattern: str = "*",
        recursive: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute directory operation.
        
        Args:
            action: Action to perform (list, create, delete)
            dirpath: Directory path
            pattern: File pattern for listing
            recursive: Whether to list recursively
            **kwargs: Additional parameters
        
        Returns:
            Operation result with file/directory information
        """
        try:
            base = Path(self.config.base_path)
            path = base / dirpath
            
            if action == "list":
                if recursive:
                    files = list(path.rglob(pattern))
                else:
                    files = list(path.glob(pattern))
                
                return {
                    "status": "success",
                    "action": "list",
                    "dirpath": str(path),
                    "files": [
                        {
                            "path": str(f.relative_to(base)),
                            "name": f.name,
                            "type": "directory" if f.is_dir() else "file",
                            "size": f.stat().st_size if f.is_file() else 0
                        }
                        for f in sorted(files)
                    ],
                    "count": len(files)
                }
            
            elif action == "create":
                path.mkdir(parents=True, exist_ok=True)
                return {
                    "status": "success",
                    "action": "create",
                    "dirpath": str(path)
                }
            
            elif action == "delete":
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                    return {
                        "status": "success",
                        "action": "delete",
                        "dirpath": str(path)
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Path is not a directory",
                        "dirpath": str(path)
                    }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }
        
        except Exception as e:
            logger.error(f"Directory operation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "action": action,
                "dirpath": dirpath
            }


class FileSearchTool:
    """Search for files by name and content."""
    
    name: str = "file_search"
    description: str = "Search for files by name pattern and content"
    
    def __init__(self, config: Optional[FileConfig] = None) -> None:
        """Initialize file search tool."""
        self.config = config or FileConfig()
    
    def execute(
        self,
        query: str,
        search_type: str = "name",
        dirpath: str = ".",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Search for files.
        
        Args:
            query: Search query (pattern or text)
            search_type: Type of search ('name' or 'content')
            dirpath: Directory to search in
            **kwargs: Additional parameters
        
        Returns:
            List of matching files
        """
        try:
            base = Path(self.config.base_path)
            path = base / dirpath
            
            matches = []
            
            if search_type == "name":
                # Search by filename pattern
                for file in path.rglob(query):
                    if file.is_file():
                        matches.append({
                            "path": str(file.relative_to(base)),
                            "name": file.name,
                            "size": file.stat().st_size
                        })
            
            elif search_type == "content":
                # Search within file contents
                for file in path.rglob("*"):
                    if file.is_file():
                        try:
                            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query.lower() in content.lower():
                                    matches.append({
                                        "path": str(file.relative_to(base)),
                                        "name": file.name,
                                        "size": file.stat().st_size
                                    })
                        except Exception:
                            continue
            
            return {
                "status": "success",
                "query": query,
                "search_type": search_type,
                "matches": matches,
                "count": len(matches)
            }
        
        except Exception as e:
            logger.error(f"File search failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "matches": []
            }


def file_reader_tool(config: Optional[Dict[str, Any]] = None) -> FileReaderTool:
    """Factory function for file reader tool."""
    cfg = FileConfig(**config) if config else FileConfig()
    return FileReaderTool(cfg)


def file_writer_tool(config: Optional[Dict[str, Any]] = None) -> FileWriterTool:
    """Factory function for file writer tool."""
    cfg = FileConfig(**config) if config else FileConfig()
    return FileWriterTool(cfg)


def directory_tool(config: Optional[Dict[str, Any]] = None) -> DirectoryTool:
    """Factory function for directory tool."""
    cfg = FileConfig(**config) if config else FileConfig()
    return DirectoryTool(cfg)


def file_search_tool(config: Optional[Dict[str, Any]] = None) -> FileSearchTool:
    """Factory function for file search tool."""
    cfg = FileConfig(**config) if config else FileConfig()
    return FileSearchTool(cfg)


__all__ = [
    "FileConfig",
    "FileReaderTool",
    "FileWriterTool",
    "DirectoryTool",
    "FileSearchTool",
    "file_reader_tool",
    "file_writer_tool",
    "directory_tool",
    "file_search_tool",
]
