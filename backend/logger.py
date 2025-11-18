"""
Workflow execution logging module.

This module provides the WorkflowLogger class for tracking workflow executions,
individual actions within workflows, and querying execution history for the UI.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from database import WorkflowExecution, Workflow

logger = logging.getLogger(__name__)


class WorkflowLogger:
    """
    Manages logging of workflow executions to the database.

    This class provides methods to create execution logs, update execution status,
    log individual actions, and query execution history for display in the UI.
    """

    def __init__(self, db: Session):
        """
        Initialize the WorkflowLogger.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)

    def start_execution(
        self,
        workflow_id: int,
        model_used: Optional[str] = None
    ) -> WorkflowExecution:
        """
        Create a new workflow execution log entry.

        Args:
            workflow_id: ID of the workflow being executed
            model_used: Name of the LLM model being used (if applicable)

        Returns:
            WorkflowExecution: The created execution record
        """
        try:
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                status="running",
                started_at=datetime.utcnow(),
                model_used=model_used,
                actions_executed=[],
                results={}
            )

            self.db.add(execution)
            self.db.commit()
            self.db.refresh(execution)

            self.logger.info(f"Started execution {execution.id} for workflow {workflow_id}")

            return execution

        except Exception as e:
            self.logger.error(f"Failed to start execution log: {e}", exc_info=True)
            self.db.rollback()
            raise

    def log_action(
        self,
        execution_id: int,
        action_name: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log an individual action within a workflow execution.

        Args:
            execution_id: ID of the workflow execution
            action_name: Name of the action being logged
            status: Action status (success/failed/skipped)
            result: Action result data
            error_message: Error message if action failed
        """
        try:
            execution = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.id == execution_id
            ).first()

            if not execution:
                self.logger.error(f"Execution {execution_id} not found")
                return

            # Append to actions_executed array
            action_log = {
                "action": action_name,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "result": result,
                "error": error_message
            }

            if execution.actions_executed is None:
                execution.actions_executed = []

            execution.actions_executed.append(action_log)

            # Mark as modified to trigger SQLAlchemy update
            self.db.add(execution)
            self.db.commit()

            self.logger.info(
                f"Logged action '{action_name}' for execution {execution_id}: {status}"
            )

        except Exception as e:
            self.logger.error(f"Failed to log action: {e}", exc_info=True)
            self.db.rollback()

    def complete_execution(
        self,
        execution_id: int,
        status: str,
        results: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        tokens_used: Optional[int] = None
    ) -> None:
        """
        Mark a workflow execution as completed.

        Args:
            execution_id: ID of the workflow execution
            status: Final status (success/failed)
            results: Final execution results
            error_message: Error message if execution failed
            tokens_used: Total tokens consumed by LLM calls
        """
        try:
            execution = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.id == execution_id
            ).first()

            if not execution:
                self.logger.error(f"Execution {execution_id} not found")
                return

            execution.status = status
            execution.completed_at = datetime.utcnow()
            execution.results = results or {}
            execution.error_message = error_message
            execution.tokens_used = tokens_used

            # Update workflow's last_run timestamp
            workflow = self.db.query(Workflow).filter(
                Workflow.id == execution.workflow_id
            ).first()

            if workflow:
                workflow.last_run = datetime.utcnow()

            self.db.commit()

            self.logger.info(
                f"Completed execution {execution_id} with status: {status}"
            )

        except Exception as e:
            self.logger.error(f"Failed to complete execution: {e}", exc_info=True)
            self.db.rollback()

    def get_recent_executions(
        self,
        workflow_id: Optional[int] = None,
        limit: int = 50
    ) -> List[WorkflowExecution]:
        """
        Retrieve recent workflow executions for UI display.

        Args:
            workflow_id: Filter by specific workflow ID (optional)
            limit: Maximum number of executions to return

        Returns:
            List[WorkflowExecution]: Recent execution records
        """
        try:
            query = self.db.query(WorkflowExecution)

            if workflow_id is not None:
                query = query.filter(WorkflowExecution.workflow_id == workflow_id)

            executions = query.order_by(
                WorkflowExecution.started_at.desc()
            ).limit(limit).all()

            return executions

        except Exception as e:
            self.logger.error(f"Failed to fetch recent executions: {e}", exc_info=True)
            return []

    def get_executions_by_status(
        self,
        status: str,
        workflow_id: Optional[int] = None,
        limit: int = 50
    ) -> List[WorkflowExecution]:
        """
        Retrieve workflow executions filtered by status.

        Args:
            status: Execution status to filter by (pending/running/success/failed)
            workflow_id: Filter by specific workflow ID (optional)
            limit: Maximum number of executions to return

        Returns:
            List[WorkflowExecution]: Filtered execution records
        """
        try:
            query = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.status == status
            )

            if workflow_id is not None:
                query = query.filter(WorkflowExecution.workflow_id == workflow_id)

            executions = query.order_by(
                WorkflowExecution.started_at.desc()
            ).limit(limit).all()

            return executions

        except Exception as e:
            self.logger.error(
                f"Failed to fetch executions by status '{status}': {e}",
                exc_info=True
            )
            return []

    def get_execution_stats(self, workflow_id: int) -> Dict[str, Any]:
        """
        Get execution statistics for a specific workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Dict containing execution statistics (total, success, failed, avg_duration)
        """
        try:
            executions = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.workflow_id == workflow_id
            ).all()

            total = len(executions)
            success_count = sum(1 for e in executions if e.status == "success")
            failed_count = sum(1 for e in executions if e.status == "failed")

            # Calculate average duration for completed executions
            completed = [
                e for e in executions
                if e.completed_at is not None and e.started_at is not None
            ]

            if completed:
                durations = [
                    (e.completed_at - e.started_at).total_seconds()
                    for e in completed
                ]
                avg_duration = sum(durations) / len(durations)
            else:
                avg_duration = 0.0

            return {
                "total_executions": total,
                "successful": success_count,
                "failed": failed_count,
                "running": total - success_count - failed_count,
                "avg_duration_seconds": round(avg_duration, 2),
                "success_rate": round(success_count / total * 100, 2) if total > 0 else 0.0
            }

        except Exception as e:
            self.logger.error(
                f"Failed to calculate execution stats for workflow {workflow_id}: {e}",
                exc_info=True
            )
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "running": 0,
                "avg_duration_seconds": 0.0,
                "success_rate": 0.0
            }


def get_workflow_logger(db: Session) -> WorkflowLogger:
    """
    Factory function to create a WorkflowLogger instance.

    Args:
        db: SQLAlchemy database session

    Returns:
        WorkflowLogger: Logger instance
    """
    return WorkflowLogger(db)
