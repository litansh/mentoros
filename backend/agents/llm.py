from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    async def generate_json(self, system_prompt: str, user_prompt: str, model: str = "gpt-4") -> Dict[str, Any]:
        """
        Generates JSON output from an LLM.
        Stub implementation for MVP.
        """
        logger.info(f"Mock LLM Call: {model}")
        # In real impl: call OpenAI/Anthropic API
        
        # MOCK RESPONSE for testing "Learn Python" goal
        return {
            "program_title": "Python Mastery",
            "duration_weeks": 4,
            "weekly_load_minutes": 120,
            "description": "A focused intro to Python.",
            "modules": [
                {
                    "week_number": 1,
                    "title": "Basics",
                    "objectives": ["Install Python", "Variables"],
                    "tasks": [
                        {
                            "type": "READING",
                            "title": "Official Docs",
                            "estimated_minutes": 30,
                            "resources": [
                                {"url": "https://docs.python.org/3/tutorial/", "title": "Tutorial", "is_paid": False}
                            ]
                        }
                    ],
                    "assessment": {"quiz_count": 5, "scenario_required": False}
                }
            ],
            "milestones": {"week2": "Functions", "week4": "Project"}
        }

llm_client = LLMClient()
