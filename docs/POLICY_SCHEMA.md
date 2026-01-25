# docs/POLICY_SCHEMA.md
MentorOS Policies (JSON Schema + Rules)
Version: 1.0

Policies are the central mechanism that makes MentorOS configurable and safe.
All policies are configurable in Admin UI and enforced server-side.

---

## 1) Policy Categories

### 1.1 BudgetPolicy
Controls paid resources and certification costs.

Fields:
- monthly_budget_cap_usd (number)
- allow_paid_resources (bool)
- paid_requires_explicit_opt_in (bool) default true
- allowed_providers (string[]) optional
- blocked_providers (string[]) optional

Rules:
- If allow_paid_resources=false -> no paid links suggested.
- If a plan includes paid items -> must show cost summary + request approval.

---

### 1.2 TokenPolicy
Controls LLM usage cost.

Fields:
- model_map:
  - planning_model
  - mentor_model
  - coach_model
  - cheap_model
- user_daily_token_cap
- user_weekly_token_cap
- on_exceed_action: degrade|block|ask_to_wait
- caching_enabled (bool)

Rules:
- Degrade to cheap_model when cap exceeded.
- Do not promise future outputs; respond with a smaller action if blocked.

---

### 1.3 CertificationPolicy
Controls certification preference and allowed certification behaviors.

Fields:
- allow_certification_tracks (bool)
- default_cert_mode: skill_first|cert_assisted|cert_first
- allow_cert_first (bool)
- require_official_objectives_link (bool) default true
- max_cert_cost_usd (number) optional
- allowed_cert_providers (string[]) optional

Rules:
- Cert-first requires official objectives links and verification.
- Any cost increase triggers explicit user confirmation.

---

### 1.4 ChannelPolicy
Controls which channels can be used and how.

Fields:
- enabled_channels: web|telegram|whatsapp|email[]
- whatsapp_provider: twilio|meta|none
- reminder_cadence_defaults:
  - reminders_per_week
  - weekly_summary_day
- max_messages_per_day_per_user
- quiet_hours:
  - start_time_local
  - end_time_local

Rules:
- Never exceed max_messages_per_day_per_user.
- Respect quiet_hours per user timezone.

---

### 1.5 VerificationPolicy
Controls link validation strictness.

Fields:
- require_verification_for_all_links (bool) default true
- verification_ttl_days (number) default 14
- allow_paywalled_links (bool) default true
- allowed_domains (string[]) optional (for cert-first strict mode)
- blocked_domains (string[]) optional

Rules:
- If require_verification_for_all_links=true -> no URL is sent without verified_status=OK.

---

### 1.6 ContentSafetyPolicy (Guardrails)
Controls how the agent behaves and what it must never do.

Fields:
- never_request_sensitive_secrets (bool) default true
- disallow_medical_legal_financial_advice_without_disclaimer (bool) default true
- require_user_approval_for_paid_actions (bool) default true
- prohibit_hallucinated_credentials_or_certification_claims (bool) default true

Rules:
- Never request passwords, tokens, 2FA codes.
- If user asks for high-stakes advice, provide general info and recommend professional advice.

---

## 2) Policy Precedence
- Global (system) policies apply to all.
- Tenant/org policies override global.
- User policies override tenant where allowed.
- Program-level settings can override user settings only if user explicitly agreed.

---

## 3) Policy Change Handling
- Policy updates must be versioned.
- Active programs must revalidate against new policies.
- If new policy makes program invalid:
  - pause program
  - notify user/admin
  - propose compliant revision

---
