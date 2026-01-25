from typing import Any, Dict
from backend.core.models import User, Program, Task
from backend.agents.llm import llm_client

class Coach:
    async def generate_weekly_message(self, user: User, program: Program) -> str:
        """
        Generates the Monday morning check-in message.
        """
        # In real impl: uses LLM with context of upcoming tasks
        return f"Hey {user.name}, ready for Week {program.modules[0].week_number}? You have {len(program.modules[0].tasks)} tasks lined up."

    async def generate_reminder(self, user: User, task: Task) -> str:
        """
        Generates a friendly nudge for a specific task.
        """
        return f"Hi {user.name}, checking in on '{task.title}'. Need any help?"

class SubjectMentor:
    async def answer_question(self, user_query: str, context: Dict[str, Any]) -> str:
        """
        Answers a user question about the content.
        """
        # In real impl: RAG + LLM
        return "This is a stub answer from the Subject Mentor. Usage of RAG would happen here."

coach_agent = Coach()
mentor_agent = SubjectMentor()
