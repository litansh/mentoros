from enum import Enum
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

# --- Enums ---

class ProgramState(str, Enum):
    START = "START"
    DISCOVERY = "DISCOVERY"
    PLAN_DRAFT = "PLAN_DRAFT"
    PLAN_REVIEW = "PLAN_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    ASSESS = "ASSESS"
    ADAPT = "ADAPT"
    STALLED = "STALLED"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"

class TaskType(str, Enum):
    READING = "READING"
    VIDEO = "VIDEO"
    DRILL = "DRILL"
    REFLECTION = "REFLECTION"
    QUIZ = "QUIZ"
    PROJECT = "PROJECT"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"

class CertificationMode(str, Enum):
    SKILL_FIRST = "SKILL_FIRST"
    CERT_ASSISTED = "CERT_ASSISTED"
    CERT_FIRST = "CERT_FIRST"

class ChannelType(str, Enum):
    WEB = "WEB"
    TELEGRAM = "TELEGRAM"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"

# --- Value Objects ---

class UserProfile(BaseModel):
    goal_title: Optional[str] = None
    goal_context: Optional[str] = None
    current_level: Optional[str] = None
    deadline: Optional[datetime] = None
    time_per_week_minutes: Optional[int] = None
    budget_cap_monthly_usd: Optional[float] = None
    flexibility_constraints: Optional[str] = None
    learning_style: Optional[str] = None
    certification_mode: CertificationMode = CertificationMode.SKILL_FIRST
    channel_preferences: List[ChannelType] = Field(default_factory=list)
    timezone: str = "UTC"

class Resource(BaseModel):
    url: HttpUrl
    title: str
    provider: Optional[str] = None
    is_paid: bool = False
    cost_usd: float = 0.0
    verification_status: VerificationStatus = VerificationStatus.PENDING
    last_verified_at: Optional[datetime] = None

# --- Entities ---

class Task(BaseModel):
    id: str
    week_number: int
    title: str
    description: Optional[str] = None
    type: TaskType
    estimated_minutes: int
    resources: List[Resource] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    completed_at: Optional[datetime] = None
    deliverable: Optional[str] = None # Description of what to submit

class Assessment(BaseModel):
    id: str
    module_id: str
    title: str
    quiz_questions: List[Dict[str, Any]] = Field(default_factory=list)
    scenario_prompt: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    completed_at: Optional[datetime] = None

class Module(BaseModel):
    id: str
    week_number: int
    title: str
    objectives: List[str] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    assessment: Optional[Assessment] = None
    is_completed: bool = False

class Program(BaseModel):
    id: str
    user_id: str
    title: str
    state: ProgramState = ProgramState.START
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    
    # Plan details
    description: Optional[str] = None
    modules: List[Module] = Field(default_factory=list)
    microns_per_week: int = 0 # load estimate
    
    # Policies snapshot (embedded for immutability)
    active_policies: Dict[str, Any] = Field(default_factory=dict)

class User(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    profile: UserProfile = Field(default_factory=UserProfile)
    # Channel specific IDs
    telegram_id: Optional[str] = None
    whatsapp_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    is_paused: bool = False
    is_disabled: bool = False

