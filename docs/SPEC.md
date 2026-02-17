# MentorOS – Architect README (Closed Spec)
Goal-first Personal Learning + Coaching Agent.
Builds a custom syllabus/roadmap per user goal and constraints, verifies resources, coaches execution, runs assessments, adapts over time, and exports artifacts (Notion/PDF). Supports configurable channels (Web + optional WhatsApp/Telegram/Email) and certification preferences (skill-first ↔ certification-first). Includes an admin control plane with RBAC, policies, and cost governance.

---

## 0) Executive Summary
MentorOS is not a course marketplace and not a generic chatbot.
MentorOS is a **goal-to-mastery system** with:
- structured onboarding
- plan generation with approval gate
- execution coaching + accountability
- assessments + adaptation
- verified resources only
- exports and reporting
- admin governance (users, roles, policies, costs)

This spec supports:
- Minimal/no-AWS deployment for MVP
- Full AWS scale deployment for growth
- Multi-channel IO where WhatsApp is optional (a channel), not the product

---

## 1) Core Concepts (Domain Model)
### Entities
- **User**: a learner with preferences and channel bindings
- **Goal**: what the user wants to achieve, with constraints
- **Program**: an approved plan (syllabus + schedule + modules)
- **Module**: weekly unit with tasks and assessments
- **Task**: reading/video/drill/reflection/quiz
- **Assessment**: quiz + scenario grading
- **Artifact**: exports (Notion/PDF/certificate)
- **Policy**: budget/token/cert/channel/provider rules enforced system-wide or per org/user
- **Resource Registry**: curated canonical sources with verification status

### Invariants (Hard Rules)
1) No Program becomes ACTIVE without explicit user approval.
2) No external link is sent unless verified or sourced from a trusted registry and verified within TTL.
3) Paid resources/certifications require explicit opt-in (unless admin policy allows auto-suggest).
4) Budget and token caps are enforced per user/program/time-window.
5) Admin actions are RBAC-protected and audited.

---

## 2) Interfaces (Channels) – Configurable
### Primary: Web UI (Home)
- onboarding wizard
- plan preview/revision/approval
- tasks dashboard + completion
- ask mentor (Q&A)
- assessments UI
- progress + readiness
- exports center
- settings: channels, reminders, certification mode, learning style

### Secondary: Messaging (Accountability)
Messaging is for reminders + short check-ins; deep learning remains in Web.

Supported adapters (pluggable):
- Telegram (free, easiest)
- WhatsApp via Twilio OR Meta Cloud API (optional)
- Email (fallback)
Future: Slack/Discord

---

## 3) Certification Preferences – Configurable
Certification behavior is a **program-level setting** (not a catalog UI).

Modes:
- **Skill-first (default):** best learning path under constraints, favors free/low-cost resources.
- **Cert-assisted:** suggests relevant certifications if cost/time fit; user chooses.
- **Cert-first (premium):** user prioritizes prestigious certs; roadmap includes objectives, practice exams, milestones.

Rules:
- Paid cert/course suggestions require explicit user approval.
- Admin can enforce:
  - allowed certification providers
  - max paid spend per month/program
  - blocklists (e.g., “no vendor X”)

---

## 4) Admin Control Plane (Web UI) – RBAC + Governance
Everything important is configurable in Admin UI.

### 4.1 Admin Features (MVP)
Users:
- list/search users
- view user profile + active program + progress + last activity
- pause/resume program
- reset state
- disable user
- force plan regeneration (with reason logged)

Policies:
- set global budget caps
- set token caps and model routing rules
- set certification policy defaults (skill-first/cert-assisted/cert-first availability)
- provider allowlist/blocklist
- channel enablement per tenant/user

Channels:
- connect provider credentials (Twilio/Meta/Telegram/Email)
- template management (message formats)
- channel health checks

Costs:
- per-user estimated monthly LLM cost
- total burn estimate
- top cost drivers by feature (Q&A, plan gen, assessments, exports)

Audit:
- immutable admin audit log (who/what/when)

### 4.2 Roles & Permissions (RBAC)
Initial roles:
- **Owner** (you): all access including secrets and billing settings
- **Admin**: user management + programs, no secrets (optional)
- **Coach**: can interact with users’ programs, no policies/secrets (optional)
- **User**: self only

RBAC must be enforced server-side for every admin endpoint.
Secrets never exposed to non-owner roles.

---

## 5) Architecture – Services
### 5.1 Core Services
- **Core API (FastAPI)**
  - state machine + program lifecycle
  - multi-agent orchestrator
  - curriculum engine
  - assessment engine
  - verification engine
  - exports (Notion/PDF/certificate)
  - admin APIs (RBAC + audit)
  - channel dispatch abstraction

- **Worker/Jobs**
  - reminders + follow-ups
  - weekly summaries
  - exports generation
  - verification refresh jobs

- **Channel Adapters**
  - Telegram adapter
  - WhatsApp adapter (Twilio/Meta)
  - Email adapter

### 5.2 Data Stores
- Postgres: canonical state (users/goals/programs/tasks/policies/audit)
- Redis/Queue: optional for jobs/rate limiting (recommended at scale)
- Object storage: artifacts (PDFs, certificates)

---

## 6) Multi-Agent Orchestration (Logical Roles)
Implemented via specialized prompts + router; can share one LLM.

Roles:
1) **Learning Architect**
   - goal -> structured syllabus JSON
   - dependency ordering, pacing, workload estimate
   - respects constraints + certification mode + policy gates

2) **Subject Mentor**
   - teaches and answers questions
   - creates examples and drills
   - avoids scope drift; references the program context

3) **Coach & Accountability**
   - weekly check-ins
   - nudges and rescheduling
   - reflection prompts
   - stall detection + recovery tactics

4) **Verifier / Guardrails (mandatory)**
   - validates links, claims, provider trust, certification constraints
   - enforces budgets/token caps
   - blocks hallucinations of resources and “facts”

---

## 7) Trust Layer – Resource Registry + Link Verification (Mandatory)
### 7.1 Registry
`resources/registry.yaml` contains canonical resources:
- title, url, provider
- tags/topics
- cost_type: free|low|paid
- cert_relevance: none|helpful|required
- trust_score
- language
- notes

Optional:
`resources/certification_catalog.yaml`
- certification name, provider, official objectives URL, prerequisites, estimated cost, renewal rules

### 7.2 Verification Rules
- Every external URL must be verified before sending.
- Verification method:
  - HEAD with redirects
  - GET fallback if HEAD blocked
- Cache verification result with TTL (e.g., 14 days)
- If invalid:
  - replace with alternative from registry
  - or ask user preference (free/paid/provider)

Hard rule:
- system must never send an unverified external link.

---

## 8) Program Lifecycle (State Machine)
States:
1) START
2) DISCOVERY (onboarding)
3) PLAN_DRAFT
4) PLAN_REVIEW
5) APPROVED
6) ACTIVE
7) ASSESS
8) ADAPT
9) COMPLETE

Triggers:
- PLAN_DRAFT: after discovery completion
- APPROVED: user explicitly approves
- ASSESS: end of module or on-demand
- ADAPT: assessment results, stalling, user time change, or goal change
- COMPLETE: program completion threshold met + final summary generated

Stall detection (configurable):
- no completion events for N days
- missed 2 reminders
- repeated quiz scores below threshold

---

## 9) Cost Governance (≤ $50/user/month Target)
LLM cost is the main variable.

### 9.1 Model Routing Policy
- cheap model: reminders, formatting, simple Q&A
- strong model: plan generation, complex Q&A, assessment feedback synthesis

### 9.2 Token Budgets
Enforced caps per user:
- daily tokens
- weekly tokens
- monthly tokens (optional)
Hard actions on exceed:
- degrade to cheap model
- restrict deep mentor features temporarily
- prompt user to continue next day / upgrade tier

### 9.3 Caching
- cached explanations by topic
- cached plan fragments
- cached verification results
- batch weekly summaries

Admin UI must expose estimated costs.

---

## 10) Deployment Modes

### Mode A: Minimal / Low-cost
Goal: ship fast, low ops.
- Web UI: Vercel
- API: Fly.io/Render
- DB: Supabase/Neon Postgres
- Jobs: GitHub Actions cron OR a worker service on Fly/Render
- Storage: Supabase Storage or Cloudflare R2
- Channels: Telegram + Email; WhatsApp optional

### Mode B: Full AWS Scale
Goal: handle growth and spikes reliably.

Recommended (container-first):
- API: ECS Fargate + ALB
- Workers: ECS Fargate
- Queue: SQS
- Scheduler: EventBridge
- DB: Aurora Serverless v2 (Postgres)
- Cache/rate limits: ElastiCache Redis (optional)
- Storage: S3 + CloudFront
- Secrets: Secrets Manager
- Observability: CloudWatch (+ OTel optional)
- WAF optional

Migration design:
- Postgres-compatible in minimal mode to ease DB migration
- job abstraction (cron vs queue)
- storage abstraction (R2/Supabase vs S3)

---

## 11) Repository Structure
.
├─ apps/
│  ├─ web/                        # Next.js (User + Admin portals)
│  ├─ api/                        # FastAPI
│  └─ worker/                     # jobs: reminders, exports, verification
├─ core/
│  ├─ orchestration/              # state machine + routing
│  ├─ agents/                     # prompts + policies
│  ├─ curriculum/                 # plan builder + cert planner
│  ├─ coaching/                   # nudges, checkins, stall logic
│  ├─ assessments/                # quizzes, scenario grading
│  ├─ verification/               # registry + link verification
│  ├─ channels/                   # telegram/whatsapp/email adapters
│  ├─ auth/                       # RBAC, sessions, owner controls
│  ├─ admin/                      # admin services + audit logs
│  └─ exports/                    # Notion/PDF/certificate generators
├─ resources/
│  ├─ registry.yaml
│  └─ certification_catalog.yaml
├─ infra/
│  ├─ minimal/
│  └─ aws_full/
└─ README.md

---

## 12) API Surface (Minimum)

User:
- POST /api/onboarding/answer
- POST /api/plan/generate
- POST /api/plan/revise
- POST /api/plan/approve
- GET  /api/program/current
- POST /api/task/complete
- POST /api/ask
- POST /api/assessment/submit
- POST /api/export/notion
- POST /api/export/pdf
- POST /api/export/certificate

Channels:
- POST /webhooks/telegram
- POST /webhooks/whatsapp/twilio (optional)
- POST /webhooks/whatsapp/meta (optional)
- POST /webhooks/email (optional)

Admin (RBAC):
- GET  /admin/users
- GET  /admin/users/{id}
- POST /admin/users/{id}/pause
- POST /admin/users/{id}/resume
- POST /admin/users/{id}/reset
- POST /admin/users/{id}/disable
- GET  /admin/policies
- POST /admin/policies/update
- GET  /admin/channels/status
- POST /admin/channels/configure
- GET  /admin/costs/summary
- GET  /admin/audit

---

## 13) Acceptance Criteria (Architect-level)

Functional:
- onboarding completes end-to-end
- plan generation respects: time/week + deadline + budget + cert-mode
- explicit approval gate works
- tasks delivered + tracked
- at least 1 assessment per module with scoring/feedback
- adaptation occurs based on assessment or stalling triggers
- export works (Notion or PDF; ideally both)

Trust:
- no unverified external links are sent
- paid resources/certs require explicit user opt-in
- verifier blocks policy violations

Governance:
- admin can pause/disable users
- RBAC enforced server-side
- admin actions logged

Scale readiness:
- minimal deployment works
- aws_full infra module documented and compatible
- job abstraction allows cron→EventBridge/SQS migration without code rewrite

---

## 14) Build Order (Safe & Practical)

1) DB schema + core state machine
2) Web onboarding + plan approval UX
3) Plan generation (Learning Architect) + verifier + registry
4) Task dashboard + completion tracking
5) Telegram channel (send/receive)
6) Jobs: reminders + weekly summaries
7) Assessments + scoring
8) Adaptation loop
9) Admin portal (RBAC + policies + audit)
10) Notion export
11) PDF export + internal certificate
12) WhatsApp adapter (optional)
13) Full AWS Terraform module
---
