"""
AI Assistant Backend - Local-first AI assistant with Ollama and MCP integration.

This package provides the MVP foundation for a local AI assistant that:
- Uses Ollama for local LLM inference
- Detects hardware for optimal model selection
- Manages conversations and chat history
- Will integrate with Gmail, Calendar, and Salesforce via MCP (future phases)

Version: 0.1.0 (MVP)
"""

__version__ = "0.1.0"
__author__ = "AI Assistant Team"

from database import init_db, get_db
from hardware_detector import get_hardware_detector
from conversation_manager import get_conversation_manager

__all__ = [
    "init_db",
    "get_db",
    "get_hardware_detector",
    "get_conversation_manager",
]
