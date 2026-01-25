from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from backend.core.models import Program, ProgramState, User

logger = logging.getLogger(__name__)

class StateTransitionError(Exception):
    pass

class ProgramStateMachine:
    """
    Manages the lifecycle of a Program.
    Enforces valid state transitions and triggers side-effects.
    """
    
    # Valid transitions map
    TRANSITIONS: Dict[ProgramState, List[ProgramState]] = {
        ProgramState.START: [ProgramState.DISCOVERY],
        ProgramState.DISCOVERY: [ProgramState.PLAN_DRAFT],
        ProgramState.PLAN_DRAFT: [ProgramState.PLAN_REVIEW],
        ProgramState.PLAN_REVIEW: [ProgramState.APPROVED, ProgramState.PLAN_DRAFT, ProgramState.START],
        ProgramState.APPROVED: [ProgramState.ACTIVE],
        ProgramState.ACTIVE: [ProgramState.ASSESS, ProgramState.STALLED, ProgramState.PAUSED, ProgramState.COMPLETE],
        ProgramState.ASSESS: [ProgramState.ADAPT, ProgramState.ACTIVE],
        ProgramState.ADAPT: [ProgramState.ACTIVE],
        ProgramState.STALLED: [ProgramState.ACTIVE, ProgramState.PAUSED, ProgramState.PLAN_REVIEW],
        ProgramState.PAUSED: [ProgramState.ACTIVE, ProgramState.COMPLETE],
        ProgramState.COMPLETE: [ProgramState.START]
    }

    def __init__(self, program: Program, user: User):
        self.program = program
        self.user = user

    def can_transition_to(self, new_state: ProgramState) -> bool:
        allowed = self.TRANSITIONS.get(self.program.state, [])
        return new_state in allowed

    async def transition_to(self, new_state: ProgramState, reason: str = None) -> Program:
        """
        Executes a transition.
        Raises StateTransitionError if invalid.
        """
        current_state = self.program.state
        
        if not self.can_transition_to(new_state):
            # Allow "self-transition" if explicitly needed? usually no.
            # But let's check if it's strictly forbidden
            raise StateTransitionError(f"Cannot transition from {current_state} to {new_state}")

        logger.info(f"Transitioning Program {self.program.id} from {current_state} to {new_state}. Reason: {reason}")
        
        # Pre-transition logic / Invariants
        if new_state == ProgramState.ACTIVE and current_state != ProgramState.APPROVED:
             # In case we missed the APPROVED step in map (we didn't, but safety check)
             # But WAIT, STALLED -> ACTIVE is valid. PAUSED -> ACTIVE is valid.
             # Only newly created programs must pass through APPROVED.
             pass

        if new_state == ProgramState.APPROVED:
             self.program.approved_at = datetime.now()

        # Update State
        self.program.state = new_state
        self.program.updated_at = datetime.now()
        
        # Post-transition logic (Side Effects triggers)
        await self._on_transition(current_state, new_state)
        
        return self.program

    async def _on_transition(self, old_state: ProgramState, new_state: ProgramState):
        """
        Hook for side effects. In a real system, this might emit events to an event bus.
        """
        if new_state == ProgramState.PLAN_DRAFT:
            # Trigger Agent to generate plan
            pass 
        elif new_state == ProgramState.ACTIVE and old_state == ProgramState.APPROVED:
            # Trigger first week modules/messages
            pass
        elif new_state == ProgramState.STALLED:
            # Trigger "re-engagement" flow
            pass
