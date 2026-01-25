from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import time

from backend.core.models import CertificationMode, ChannelType

class BudgetPolicy(BaseModel):
    monthly_budget_cap_usd: float = 0.0
    allow_paid_resources: bool = False
    paid_requires_explicit_opt_in: bool = True
    allowed_providers: List[str] = Field(default_factory=list)
    blocked_providers: List[str] = Field(default_factory=list)

class TokenPolicy(BaseModel):
    model_map: Dict[str, str] = Field(default_factory=lambda: {
        "planning_model": "gpt-4",
        "mentor_model": "gpt-4",
        "coach_model": "gpt-3.5-turbo",
        "cheap_model": "gpt-3.5-turbo"
    })
    user_daily_token_cap: int = 100000
    user_weekly_token_cap: int = 500000
    on_exceed_action: str = "degrade" # degrade | block | ask_to_wait
    caching_enabled: bool = True

class CertificationPolicy(BaseModel):
    allow_certification_tracks: bool = True
    default_cert_mode: CertificationMode = CertificationMode.SKILL_FIRST
    allow_cert_first: bool = False
    require_official_objectives_link: bool = True
    max_cert_cost_usd: Optional[float] = None
    allowed_cert_providers: List[str] = Field(default_factory=list)

class ChannelPolicy(BaseModel):
    enabled_channels: List[ChannelType] = Field(default_factory=lambda: [ChannelType.WEB])
    whatsapp_provider: str = "none" # twilio | meta | none
    reminder_cadence_defaults: Dict[str, int] = Field(default_factory=lambda: {
        "reminders_per_week": 3,
        "weekly_summary_day": 0 # Sunday
    })
    max_messages_per_day_per_user: int = 5
    quiet_hours_start: time = time(22, 0) # 10 PM
    quiet_hours_end: time = time(8, 0)   # 8 AM

class VerificationPolicy(BaseModel):
    require_verification_for_all_links: bool = True
    verification_ttl_days: int = 14
    allow_paywalled_links: bool = True
    allowed_domains: List[str] = Field(default_factory=list)
    blocked_domains: List[str] = Field(default_factory=list)

class ContentSafetyPolicy(BaseModel):
    never_request_sensitive_secrets: bool = True
    disallow_medical_legal_financial_advice_without_disclaimer: bool = True
    require_user_approval_for_paid_actions: bool = True
    prohibit_hallucinated_credentials_or_certification_claims: bool = True

class GlobalPolicy(BaseModel):
    budget: BudgetPolicy = Field(default_factory=BudgetPolicy)
    token: TokenPolicy = Field(default_factory=TokenPolicy)
    certification: CertificationPolicy = Field(default_factory=CertificationPolicy)
    channel: ChannelPolicy = Field(default_factory=ChannelPolicy)
    verification: VerificationPolicy = Field(default_factory=VerificationPolicy)
    safety: ContentSafetyPolicy = Field(default_factory=ContentSafetyPolicy)
