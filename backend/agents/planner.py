import uuid
from datetime import datetime
from typing import List

from backend.core.models import User, Program, Module, Task, Resource, TaskType, TaskStatus, ProgramState
from backend.core.policies import GlobalPolicy
from backend.agents.prompts import PLANNING_SYSTEM_PROMPT
from backend.agents.llm import llm_client
from backend.verification.engine import verifier

class LearningArchitect:
    def __init__(self, policy: GlobalPolicy):
        self.policy = policy
    
    async def generate_plan(self, user: User) -> Program:
        # 1. Prepare Prompt
        system_prompt = PLANNING_SYSTEM_PROMPT.format(
            goal_title=user.profile.goal_title,
            goal_context=user.profile.goal_context,
            current_level=user.profile.current_level,
            time_per_week_minutes=user.profile.time_per_week_minutes,
            certification_mode=user.profile.certification_mode,
            budget_cap_monthly_usd=user.profile.budget_cap_monthly_usd,
            policies_json=self.policy.model_dump_json()
        )
        
        # 2. Call LLM
        # In a real scenario, we'd pass user inputs. For now the prompt has context.
        plan_json = await llm_client.generate_json(system_prompt, "Generate plan")
        
        # 3. Parse and Verify
        # We need to verify all links before creating the Program object 
        # (or create it and then update status)
        
        modules: List[Module] = []
        for m_data in plan_json.get("modules", []):
            tasks: List[Task] = []
            for t_data in m_data.get("tasks", []):
                resources: List[Resource] = []
                for r_data in t_data.get("resources", []):
                    res = Resource(
                        url=r_data["url"],
                        title=r_data["title"],
                        is_paid=r_data.get("is_paid", False),
                        cost_usd=r_data.get("cost_usd", 0.0)
                    )
                    # Verify Link
                    await verifier.verify_resource(res)
                    resources.append(res)
                
                task = Task(
                    id=str(uuid.uuid4()),
                    week_number=m_data["week_number"],
                    title=t_data["title"],
                    description=t_data.get("description"),
                    type=TaskType(t_data["type"]),
                    estimated_minutes=t_data["estimated_minutes"],
                    resources=resources,
                    deliverable=t_data.get("deliverable")
                )
                tasks.append(task)
            
            module = Module(
                id=str(uuid.uuid4()),
                week_number=m_data["week_number"],
                title=m_data["title"],
                objectives=m_data.get("objectives", []),
                tasks=tasks
            )
            modules.append(module)
            
        # 4. Create Program Entity
        program = Program(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title=plan_json.get("program_title", "Custom Program"),
            description=plan_json.get("description"),
            state=ProgramState.PLAN_DRAFT, # Initial state
            modules=modules,
            microns_per_week=plan_json.get("weekly_load_minutes", 0),
            active_policies=self.policy.model_dump()
        )
        
        return program
