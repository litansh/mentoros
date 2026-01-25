# docs/AGENT_PROMPTS.md
MentorOS Agent Prompts (Implementation Guide)
Version: 1.0

This file is not the raw prompts; it defines how prompts must be structured and what each agent must output.
Use these rules to implement prompt templates in code.

---

## 1) Prompt Format Requirements
- All agent outputs that affect system state MUST be JSON that validates against Pydantic schemas.
- The router must reject non-JSON for plan generation and policy decisions.
- Free-form text is allowed only for user-facing messages.

---

## 2) Role: Learning Architect
### Objective
Create a structured program plan that respects constraints and policies.

### Inputs
- user onboarding profile
- active policies (budget/token/cert/channel/provider/verification)
- certification mode (skill-first/cert-assisted/cert-first)

### Output (JSON)
- program_title
- duration_weeks
- weekly_load_minutes
- modules[]:
  - week_number
  - objectives[]
  - tasks[]:
    - type
    - title
    - estimated_minutes
    - resource_links[] (may be empty until verification)
    - deliverable (what user submits)
  - assessment:
    - quiz_count
    - scenario_required (bool)
- milestones (week2/week4/week8)
- success_criteria
- paid_cost_estimate_usd (if any)
- notes_for_coach

Rules
- Must stay within time_per_week constraint.
- Must not include paid resources unless allowed by BudgetPolicy.
- Must include assessments cadence.

---

## 3) Role: Subject Mentor
### Objective
Teach and support execution of the current module/task.

### Inputs
- active program context
- current week/module
- user question or task deliverable
- constraints (time/budget)

### Output
- user-facing explanation
- 1–3 actionable next steps
- optional drill question
- if user is stuck: propose an easier alternative within plan

---

## 4) Role: Coach & Accountability
### Objective
Maintain momentum and schedule realism.

### Inputs
- user progress
- stall signals
- reminder preferences
- quiet hours

### Output
- short check-in message
- 1 micro-action suggestion
- reschedule offer

Rules
- Never guilt the user.
- Always provide a “pause” option.

---

## 5) Role: Verifier / Guardrails
### Objective
Block hallucinations and enforce policies.

### Inputs
- links list + registry entries
- verification results
- policies

### Output (JSON)
- verified_links[]
- rejected_links[] with reason
- replacements[] from registry (if available)
- compliance_flags[] (budget violation, blocked provider, etc.)

Rules
- If verification required, reject any link not verified OK.
- If cert-first, enforce official objectives link requirement.
- If costs exceed budget, flag and require user approval.

---
