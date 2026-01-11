#!/usr/bin/env python3
"""echo_tool.py

Date: 2026-01-11
Author: cbwinslow
Summary:
  Minimal example tool for local runtime.
Inputs:
  text (str)
Outputs:
  dict: {'echo': text}
Modification Log:
  - 2026-01-11: Initial version.
"""

from __future__ import annotations
from typing import Dict

def echo_tool(text: str) -> Dict[str, str]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return {"echo": text}
