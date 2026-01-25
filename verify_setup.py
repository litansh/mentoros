import asyncio
import uuid
from datetime import datetime

# Import backend components
from backend.core.models import User, UserProfile, ChannelType, ProgramState
from backend.core.policies import GlobalPolicy
from backend.agents.planner import LearningArchitect
from backend.core.state import ProgramStateMachine
from backend.verification.engine import verifier

async def run_verification():
    print(">>> Starting Verification Script <<<")
    
    # 1. Setup User
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        profile=UserProfile(
            goal_title="Learn Python",
            goal_context="Need it for data science job",
            current_level="Beginner",
            time_per_week_minutes=300,
            channel_preferences=[ChannelType.WEB]
        )
    )
    print(f"[User] Created: {user.name} ({user.id})")

    # 2. Setup Policy
    policy = GlobalPolicy()
    print("[Policy] Initialized default policies.")

    # 3. Generate Plan (Planning Agent)
    print("[Agent] Generating plan (mock LLM)...")
    architect = LearningArchitect(policy)
    program = await architect.generate_plan(user)
    
    print(f"[Plan] Generated Program: {program.title}")
    print(f"       State: {program.state}")
    print(f"       Modules: {len(program.modules)}")
    
    # Verify resources inside (Verifier)
    for module in program.modules:
        for task in module.tasks:
            for res in task.resources:
                print(f"       [Resource Check] {res.title} ({res.url}) -> {res.verification_status}")

    # 4. State Machine Transition
    print("[State] Initializing State Machine...")
    sm = ProgramStateMachine(program, user)
    
    # Draft -> Review
    await sm.transition_to(ProgramState.PLAN_REVIEW, "Plan generation complete")
    print(f"[State] Transitioned to {program.state}")
    
    # Review -> Approved (Simulate user action)
    await sm.transition_to(ProgramState.APPROVED, "User approved plan")
    print(f"[State] Transitioned to {program.state}")
    
    # Approved -> Active
    await sm.transition_to(ProgramState.ACTIVE, "System activation")
    print(f"[State] Transitioned to {program.state}")

    print(">>> Verification Complete: SUCCESS <<<")

if __name__ == "__main__":
    asyncio.run(run_verification())
