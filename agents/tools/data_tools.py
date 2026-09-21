#!/usr/bin/env python3
"""Data Processing Tools.

Tools for data transformation, analysis, and manipulation.
"""

import json
import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DataConfig(BaseModel):
    """Configuration for data tools."""

    max_records: int = Field(default=10000, gt=0, description="Max records to process")
    precision: int = Field(default=2, ge=0, description="Decimal precision")


class JSONProcessorTool:
    """Process and transform JSON data."""

    name: str = "json_processor"
    description: str = "Parse, validate, and transform JSON data"

    def __init__(self, config: DataConfig | None = None) -> None:
        """Initialize JSON processor tool."""
        self.config = config or DataConfig()

    def execute(
        self,
        data: str | dict | list,
        action: str = "parse",
        query: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Process JSON data.

        Args:
            data: JSON string or Python object
            action: Action to perform (parse, stringify, query, validate)
            query: JSON path query for filtering
            **kwargs: Additional parameters

        Returns:
            Processed data result
        """
        try:
            if action == "parse":
                if isinstance(data, str):
                    parsed = json.loads(data)
                else:
                    parsed = data
                return {
                    "status": "success",
                    "action": "parse",
                    "data": parsed,
                    "type": type(parsed).__name__,
                }

            elif action == "stringify":
                stringified = json.dumps(data, indent=2)
                return {
                    "status": "success",
                    "action": "stringify",
                    "data": stringified,
                    "size": len(stringified),
                }

            elif action == "validate":
                try:
                    if isinstance(data, str):
                        json.loads(data)
                    else:
                        json.dumps(data)
                    return {"status": "success", "action": "validate", "valid": True}
                except json.JSONDecodeError as e:
                    return {
                        "status": "success",
                        "action": "validate",
                        "valid": False,
                        "error": str(e),
                    }

            elif action == "query":
                # Simple JSON path query
                if isinstance(data, str):
                    data = json.loads(data)

                if query:
                    result = self._json_path_query(data, query)
                else:
                    result = data

                return {"status": "success", "action": "query", "query": query, "result": result}

            else:
                return {"status": "error", "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"JSON processing failed: {e}")
            return {"status": "error", "error": str(e), "action": action}

    def _json_path_query(self, data: Any, path: str) -> Any:
        """Simple JSON path query implementation."""
        parts = path.strip("/").split("/")
        current = data

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                current = current[idx] if idx < len(current) else None
            else:
                return None

        return current


class DataTransformTool:
    """Transform and manipulate data structures."""

    name: str = "data_transform"
    description: str = "Transform, filter, and aggregate data"

    def __init__(self, config: DataConfig | None = None) -> None:
        """Initialize data transform tool."""
        self.config = config or DataConfig()

    def execute(self, data: list[dict[str, Any]], operation: str, **kwargs: Any) -> dict[str, Any]:
        """Transform data.

        Args:
            data: List of data records
            operation: Operation to perform (filter, map, reduce, sort, group)
            **kwargs: Operation-specific parameters

        Returns:
            Transformed data result
        """
        try:
            if operation == "filter":
                condition = kwargs.get("condition", {})
                result = self._filter_data(data, condition)

            elif operation == "map":
                mapping = kwargs.get("mapping", {})
                result = self._map_data(data, mapping)

            elif operation == "sort":
                key = kwargs.get("key", "")
                reverse = kwargs.get("reverse", False)
                result = self._sort_data(data, key, reverse)

            elif operation == "group":
                key = kwargs.get("key", "")
                result = self._group_data(data, key)

            elif operation == "aggregate":
                field = kwargs.get("field", "")
                func = kwargs.get("function", "sum")
                result = self._aggregate_data(data, field, func)

            else:
                return {"status": "error", "error": f"Unknown operation: {operation}"}

            return {
                "status": "success",
                "operation": operation,
                "result": result,
                "count": len(result) if isinstance(result, list) else 1,
            }

        except Exception as e:
            logger.error(f"Data transform failed: {e}")
            return {"status": "error", "error": str(e), "operation": operation}

    def _filter_data(self, data: list[dict], condition: dict) -> list[dict]:
        """Filter data based on condition."""
        filtered = []
        for item in data:
            match = True
            for key, value in condition.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(item)
        return filtered

    def _map_data(self, data: list[dict], mapping: dict) -> list[dict]:
        """Map data fields."""
        mapped = []
        for item in data:
            new_item = {}
            for new_key, old_key in mapping.items():
                new_item[new_key] = item.get(old_key)
            mapped.append(new_item)
        return mapped

    def _sort_data(self, data: list[dict], key: str, reverse: bool) -> list[dict]:
        """Sort data by key."""
        return sorted(data, key=lambda x: x.get(key, ""), reverse=reverse)

    def _group_data(self, data: list[dict], key: str) -> dict[str, list[dict]]:
        """Group data by key."""
        groups: dict[str, list[dict]] = {}
        for item in data:
            group_key = str(item.get(key, "unknown"))
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(item)
        return groups

    def _aggregate_data(self, data: list[dict], field: str, func: str) -> int | float:
        """Aggregate data field."""
        values = [item.get(field, 0) for item in data if isinstance(item.get(field), (int, float))]

        if func == "sum":
            return sum(values)
        elif func == "avg":
            return sum(values) / len(values) if values else 0
        elif func == "min":
            return min(values) if values else 0
        elif func == "max":
            return max(values) if values else 0
        elif func == "count":
            return len(values)
        else:
            return 0


class CSVProcessorTool:
    """Process CSV data."""

    name: str = "csv_processor"
    description: str = "Parse and transform CSV data"

    def __init__(self, config: DataConfig | None = None) -> None:
        """Initialize CSV processor tool."""
        self.config = config or DataConfig()

    def execute(
        self, data: str | list[dict], action: str = "parse", **kwargs: Any
    ) -> dict[str, Any]:
        """Process CSV data.

        Args:
            data: CSV string or list of dictionaries
            action: Action to perform (parse, stringify)
            **kwargs: Additional parameters

        Returns:
            Processed CSV result
        """
        try:
            import csv
            import io

            if action == "parse":
                if isinstance(data, str):
                    reader = csv.DictReader(io.StringIO(data))
                    records = list(reader)
                else:
                    records = data

                return {
                    "status": "success",
                    "action": "parse",
                    "records": records[: self.config.max_records],
                    "count": len(records),
                }

            elif action == "stringify":
                if not data:
                    return {"status": "error", "error": "No data to stringify"}

                output = io.StringIO()
                fieldnames = list(data[0].keys()) if isinstance(data[0], dict) else []
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

                return {
                    "status": "success",
                    "action": "stringify",
                    "csv": output.getvalue(),
                    "rows": len(data),
                }

            else:
                return {"status": "error", "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"CSV processing failed: {e}")
            return {"status": "error", "error": str(e), "action": action}


def json_processor_tool(config: dict[str, Any] | None = None) -> JSONProcessorTool:
    """Factory function for JSON processor tool."""
    cfg = DataConfig(**config) if config else DataConfig()
    return JSONProcessorTool(cfg)


def data_transform_tool(config: dict[str, Any] | None = None) -> DataTransformTool:
    """Factory function for data transform tool."""
    cfg = DataConfig(**config) if config else DataConfig()
    return DataTransformTool(cfg)


def csv_processor_tool(config: dict[str, Any] | None = None) -> CSVProcessorTool:
    """Factory function for CSV processor tool."""
    cfg = DataConfig(**config) if config else DataConfig()
    return CSVProcessorTool(cfg)


__all__ = [
    "CSVProcessorTool",
    "DataConfig",
    "DataTransformTool",
    "JSONProcessorTool",
    "csv_processor_tool",
    "data_transform_tool",
    "json_processor_tool",
]
