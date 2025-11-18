"""
Conversation management module for the AI Assistant.

This module manages conversation state, detects user intent, stores conversation
history in the database, and provides context to the LLM. This is the MVP
implementation that will be expanded in Week 2-3 to include MCP tool detection
and advanced intent recognition.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from database import Conversation, User, get_or_create_user

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation state and history for the AI Assistant.

    This class handles creating conversations, adding messages, retrieving
    conversation history, and (in future versions) detecting user intent
    for tool calls via MCP.
    """

    def __init__(self, db: Session):
        """
        Initialize the ConversationManager.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)

    def create_conversation(
        self,
        user_id: Optional[int] = None
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            user_id: User ID (optional, will create/fetch default user if not provided)

        Returns:
            Conversation: The created conversation record
        """
        try:
            # Get or create default user for MVP
            if user_id is None:
                user = get_or_create_user(self.db)
                user_id = user.id

            conversation_id = str(uuid.uuid4())

            conversation = Conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                messages=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

            self.logger.info(f"Created conversation {conversation_id}")

            return conversation

        except Exception as e:
            self.logger.error(f"Failed to create conversation: {e}", exc_info=True)
            self.db.rollback()
            raise

    def get_conversation(
        self,
        conversation_id: str
    ) -> Optional[Conversation]:
        """
        Retrieve a conversation by ID.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Optional[Conversation]: The conversation record or None if not found
        """
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()

            return conversation

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve conversation {conversation_id}: {e}",
                exc_info=True
            )
            return None

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to an existing conversation.

        Args:
            conversation_id: Unique conversation identifier
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata (model used, tokens, etc.)
        """
        try:
            conversation = self.get_conversation(conversation_id)

            if not conversation:
                self.logger.error(f"Conversation {conversation_id} not found")
                return

            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }

            if conversation.messages is None:
                conversation.messages = []

            conversation.messages.append(message)
            conversation.updated_at = datetime.utcnow()

            # Flag the messages field as modified so SQLAlchemy tracks the change
            flag_modified(conversation, "messages")

            self.db.add(conversation)
            self.db.commit()

            self.logger.info(
                f"Added {role} message to conversation {conversation_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to add message to conversation {conversation_id}: {e}",
                exc_info=True
            )
            self.db.rollback()

    def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation message history.

        Args:
            conversation_id: Unique conversation identifier
            limit: Maximum number of messages to return (most recent)

        Returns:
            List[Dict]: List of messages in chronological order
        """
        try:
            conversation = self.get_conversation(conversation_id)

            if not conversation or not conversation.messages:
                return []

            messages = conversation.messages

            # Apply limit if specified (get most recent N messages)
            if limit is not None and limit > 0:
                messages = messages[-limit:]

            return messages

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve conversation history {conversation_id}: {e}",
                exc_info=True
            )
            return []

    def get_context_for_llm(
        self,
        conversation_id: str,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get conversation context formatted for LLM input.

        Args:
            conversation_id: Unique conversation identifier
            max_messages: Maximum number of recent messages to include

        Returns:
            List[Dict]: Messages formatted for LLM (role + content only)
        """
        try:
            messages = self.get_conversation_history(
                conversation_id=conversation_id,
                limit=max_messages
            )

            # Format for LLM: only include role and content
            llm_context = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]

            return llm_context

        except Exception as e:
            self.logger.error(
                f"Failed to get LLM context for conversation {conversation_id}: {e}",
                exc_info=True
            )
            return []

    def detect_intent(
        self,
        user_message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect user intent from a message (MVP version - basic implementation).

        This is a placeholder for future MCP tool detection. In Week 2-3,
        this will be expanded to detect when the user wants to:
        - Send an email (Gmail)
        - Check calendar (Calendar)
        - Query Salesforce data
        - Create/run workflows

        Args:
            user_message: The user's message
            conversation_id: Optional conversation ID for context

        Returns:
            Dict containing:
                - intent_type: "chat" | "tool_call" | "workflow"
                - tools_needed: List of tool names
                - confidence: 0.0-1.0
        """
        # MVP: Always return "chat" intent
        # Future: Use LLM or pattern matching to detect tool usage

        # Simple keyword detection for demonstration
        message_lower = user_message.lower()

        # Email keywords
        if any(word in message_lower for word in ["email", "send", "gmail", "message"]):
            return {
                "intent_type": "tool_call",
                "tools_needed": ["gmail"],
                "confidence": 0.7,
                "note": "Email-related intent detected (placeholder)"
            }

        # Calendar keywords
        if any(word in message_lower for word in ["calendar", "schedule", "meeting", "event"]):
            return {
                "intent_type": "tool_call",
                "tools_needed": ["calendar"],
                "confidence": 0.7,
                "note": "Calendar-related intent detected (placeholder)"
            }

        # Salesforce keywords
        if any(word in message_lower for word in ["salesforce", "crm", "lead", "opportunity"]):
            return {
                "intent_type": "tool_call",
                "tools_needed": ["salesforce"],
                "confidence": 0.7,
                "note": "Salesforce-related intent detected (placeholder)"
            }

        # Workflow keywords
        if any(word in message_lower for word in ["workflow", "automate", "automation"]):
            return {
                "intent_type": "workflow",
                "tools_needed": [],
                "confidence": 0.6,
                "note": "Workflow-related intent detected (placeholder)"
            }

        # Default: chat intent
        return {
            "intent_type": "chat",
            "tools_needed": [],
            "confidence": 1.0,
            "note": "General conversation"
        }

    def get_user_conversations(
        self,
        user_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Conversation]:
        """
        Get all conversations for a user.

        Args:
            user_id: User ID (optional, will use default user if not provided)
            limit: Maximum number of conversations to return

        Returns:
            List[Conversation]: User's conversations ordered by most recent
        """
        try:
            # Get or create default user for MVP
            if user_id is None:
                user = get_or_create_user(self.db)
                user_id = user.id

            conversations = self.db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(
                Conversation.updated_at.desc()
            ).limit(limit).all()

            return conversations

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve user conversations: {e}",
                exc_info=True
            )
            return []

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            conversation = self.get_conversation(conversation_id)

            if not conversation:
                self.logger.warning(f"Conversation {conversation_id} not found for deletion")
                return False

            self.db.delete(conversation)
            self.db.commit()

            self.logger.info(f"Deleted conversation {conversation_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to delete conversation {conversation_id}: {e}",
                exc_info=True
            )
            self.db.rollback()
            return False


def get_conversation_manager(db: Session) -> ConversationManager:
    """
    Factory function to create a ConversationManager instance.

    Args:
        db: SQLAlchemy database session

    Returns:
        ConversationManager: Manager instance
    """
    return ConversationManager(db)
