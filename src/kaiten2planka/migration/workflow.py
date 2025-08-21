"""Migration workflow management."""

from typing import Dict, Any, List, Optional
from enum import Enum
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class MigrationPhase(Enum):
    """Migration phases in order."""
    AUTHENTICATION = "authentication"
    USER_DISCOVERY = "user_discovery"
    PROJECT_MIGRATION = "project_migration"
    CARD_MIGRATION = "card_migration"
    ATTACHMENT_MIGRATION = "attachment_migration"
    VERIFICATION = "verification"
    COMPLETE = "complete"


@dataclass
class PhaseResult:
    """Result of a migration phase."""
    phase: MigrationPhase
    success: bool
    duration_seconds: float
    entities_processed: int
    errors: List[str]
    metadata: Dict[str, Any]


class MigrationWorkflow:
    """Manages migration workflow and phase tracking."""
    
    def __init__(self):
        self.current_phase = MigrationPhase.AUTHENTICATION
        self.phase_results: List[PhaseResult] = []
        self.start_time = datetime.now()
    
    def start_phase(self, phase: MigrationPhase) -> None:
        """Start a new migration phase."""
        self.current_phase = phase
        logger.info(f"Starting migration phase: {phase.value}")
    
    def complete_phase(
        self, 
        phase: MigrationPhase, 
        success: bool = True,
        entities_processed: int = 0,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Complete a migration phase."""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        result = PhaseResult(
            phase=phase,
            success=success,
            duration_seconds=duration,
            entities_processed=entities_processed,
            errors=errors or [],
            metadata=metadata or {}
        )
        
        self.phase_results.append(result)
        
        status = "completed" if success else "failed"
        logger.info(f"Phase {phase.value} {status} in {duration:.2f}s")
        
        if not success:
            logger.error(f"Phase {phase.value} failed with errors: {errors}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get migration workflow summary."""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        total_entities = sum(r.entities_processed for r in self.phase_results)
        total_errors = sum(len(r.errors) for r in self.phase_results)
        
        return {
            'start_time': self.start_time.isoformat(),
            'total_duration_seconds': total_duration,
            'current_phase': self.current_phase.value,
            'phases_completed': len(self.phase_results),
            'total_entities_processed': total_entities,
            'total_errors': total_errors,
            'success_rate': (total_entities - total_errors) / max(total_entities, 1),
            'phase_results': [
                {
                    'phase': r.phase.value,
                    'success': r.success,
                    'duration_seconds': r.duration_seconds,
                    'entities_processed': r.entities_processed,
                    'error_count': len(r.errors)
                }
                for r in self.phase_results
            ]
        }
