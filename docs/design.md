# MentorOS - Architecture Decisions

This document captures key design decisions made during the development of MentorOS.

---

## 1. Multi-Agent Architecture vs Single LLM

**Decision:** Use specialized multi-agent architecture with 4 distinct agent roles.

**Context:** Need to handle diverse tasks: planning, teaching, coaching, verification.

**Alternatives:**
- Single general-purpose LLM with all prompts
- Separate fine-tuned models per task
- Rule-based system without AI

**Rationale:**
- Specialized prompts improve quality per domain (planning vs teaching)
- Easier to debug and improve individual agents
- Can use different models per agent (cheap for reminders, strong for planning)
- Simpler than fine-tuning multiple models
- More flexible than pure rules

**Trade-offs:**
- More complex orchestration logic
- Multiple API calls vs single call
- Need clear agent boundaries

**Implementation:**
- Learning Architect: Goal → syllabus with dependencies
- Subject Mentor: Q&A, examples, context-aware teaching
- Coach: Check-ins, accountability, stall detection
- Verifier/Guardrails: Policy enforcement, link validation

---

## 2. Approval-Gated Program Lifecycle

**Decision:** Require explicit human approval before any program becomes ACTIVE.

**Context:** Users need control over their learning path before committing time.

**Alternatives:**
- Auto-activate all generated programs
- Preview-only mode with opt-in
- Progressive disclosure (reveal modules gradually)

**Rationale:**
- Prevents unintended resource allocation (time, money, effort)
- Builds trust ("no surprises")
- Allows revision before commitment
- Reduces churned users who start wrong programs

**Trade-offs:**
- Extra friction (one more click)
- Requires good preview UX

**Implementation:**
- State machine: PLAN_REVIEW → user_approves() → APPROVED → ACTIVE
- Web UI shows full program preview before approval
- Clear "Approve" vs "Revise" actions

---

## 3. Resource Registry + Verification Layer

**Decision:** Maintain curated YAML registry + verify all external links before sending.

**Context:** LLMs hallucinate resources and links break over time.

**Alternatives:**
- Trust LLM-generated links directly
- Use only programmatic APIs (Udemy, Coursera, etc.)
- Wikipedia-style community curation database

**Rationale:**
- Prevents "404 Not Found" frustration
- Reduces hallucinated resources
- Curated registry ensures quality
- Cached verification (14-day TTL) balances freshness vs cost

**Trade-offs:**
- Manual registry maintenance required
- HTTP HEAD/GET overhead for verification
- Stale cache risk if resources move

**Implementation:**
- `resources/registry.yaml`: canonical sources with metadata
- Verification engine: HTTP HEAD → GET fallback → cache result
- TTL: 14 days (configurable)
- Hard rule: no unverified links sent to users

---

## 4. PostgreSQL for Canonical State

**Decision:** Use PostgreSQL as primary data store for users, programs, tasks, policies.

**Context:** Need ACID guarantees, complex queries, relational integrity.

**Alternatives:**
- MongoDB (document store)
- DynamoDB (key-value)
- SQLite (embedded)
- Redis (in-memory)

**Rationale:**
- ACID transactions for state machine transitions
- Complex joins (user → programs → modules → tasks)
- JSON columns for flexible policy/metadata
- Mature ecosystem (Alembic migrations, pgAdmin)
- Deployment flexibility (Supabase/Neon for minimal, Aurora for scale)

**Trade-offs:**
- Heavier than NoSQL for simple use cases
- Schema migrations required
- Not ideal for massive scale (but sufficient for target)

**Implementation:**
- Tables: users, goals, programs, modules, tasks, assessments, policies, audit_log
- JSON columns: policy_config, metadata
- Indexes: user_id, program_id, state, created_at

---

## 5. Cost Governance via Token Budgets

**Decision:** Enforce daily/weekly/monthly token caps per user with model routing.

**Context:** LLM costs are primary expense (~$20-50/user/month). Need control.

**Alternatives:**
- Unlimited usage (risk runaway costs)
- Hard user limits (bad UX)
- Post-usage billing only
- Subscription tiers with fixed allocations

**Rationale:**
- Prevents cost surprises for both platform and users
- Enables tiered pricing (free tier, premium tier)
- Forces cost-conscious design (use cheap models when possible)
- Admin visibility into burn rate

**Trade-offs:**
- Complexity in tracking and enforcing
- User frustration if limits hit mid-task
- Need graceful degradation (cheap model fallback)

**Implementation:**
- `DAILY_TOKEN_CAP`, `MONTHLY_BUDGET_USD` in .env
- Policy engine: check before LLM call, reject if over budget
- Model routing: cheap (reminders) → smart (plan gen) → premium (complex Q&A)
- Admin UI: per-user cost dashboard

---

## 6. State Machine for Program Lifecycle

**Decision:** Explicit state machine (9 states) with guarded transitions.

**Context:** Need predictable, auditable progression from goal to mastery.

**Alternatives:**
- Implicit states (infer from data)
- Workflow engine (Temporal, Airflow)
- Event sourcing with CQRS

**Rationale:**
- Clear semantics for each state
- Easy to debug and visualize
- Guards enforce invariants (no ACTIVE without approval)
- Simple to implement (Python Enum + switch)

**Trade-offs:**
- Less flexible than event sourcing
- State explosion risk if too granular
- Requires careful state design upfront

**Implementation:**
- States: START, DISCOVERY, PLAN_DRAFT, PLAN_REVIEW, APPROVED, ACTIVE, ASSESS, ADAPT, COMPLETE
- Transitions: `user_approves()`, `task_completed()`, `stall_detected()`, `assessment_scored()`
- Guards: `can_transition(from_state, to_state, event)`

---

## 7. Multi-Channel Architecture (Web + Messaging)

**Decision:** Web UI is primary, messaging (Telegram/WhatsApp/Email) is secondary for accountability.

**Context:** Deep learning happens on web, but reminders/check-ins need lower-friction channels.

**Alternatives:**
- Web-only (no messaging)
- Messaging-only (like WhatsApp-first bots)
- All channels equal priority

**Rationale:**
- Web UI better for:
  - Onboarding wizards
  - Plan preview/approval
  - Complex task dashboards
  - Assessments with UI
- Messaging better for:
  - Daily reminders (low friction)
  - Quick check-ins ("Did you complete today?")
  - Accountability nudges
- Not all users want WhatsApp; Telegram/Email provide alternatives

**Trade-offs:**
- Increases surface area (more UIs to maintain)
- Channel-specific UX differences
- Webhook complexity for messaging

**Implementation:**
- Channel adapters: abstract interface (`send_message()`, `receive_message()`)
- Pluggable: Telegram, WhatsApp (Twilio/Meta), Email, future (Slack/Discord)
- Web UI: Next.js with API client
- Admin UI: channel health checks and configuration

---

## 8. Certification Preferences as Program-Level Setting

**Decision:** Certification mode (skill-first, cert-assisted, cert-first) is configurable per program.

**Context:** Some users want cheap/free paths, others need prestigious certifications.

**Alternatives:**
- Global user preference (one mode for all programs)
- No certification support (skill-only)
- Certification catalog UI (browse and pick)

**Rationale:**
- Different goals need different strategies (hobby vs career transition)
- Keeps complexity in program generation, not in browsing
- Admin policies can enforce constraints (max paid spend)
- Avoids "cert marketplace" UX (not the core product)

**Trade-offs:**
- Users might not understand the modes
- Requires clear explanation in onboarding
- Adds complexity to plan generation agent

**Implementation:**
- Onboarding asks: "Do you need certifications for this goal?"
  - No → skill-first (default, favors free resources)
  - Maybe → cert-assisted (suggests relevant certs if budget/time fit)
  - Yes → cert-first (prioritizes prestigious certs, includes exam prep)
- Learning Architect respects mode + policy constraints

---

## 9. FastAPI for Backend

**Decision:** Use FastAPI for Core API.

**Context:** Need async, high-performance API with auto-docs and type safety.

**Alternatives:**
- Flask (simpler, synchronous)
- Django (batteries-included, heavier)
- Express.js (Node ecosystem)

**Rationale:**
- Async/await for LLM calls (I/O bound)
- Auto-generated Swagger docs (/docs)
- Pydantic for request/response validation
- Type hints improve maintainability
- Modern Python ecosystem

**Trade-offs:**
- Steeper learning curve than Flask
- Less mature ecosystem than Django
- No built-in ORM (use SQLAlchemy)

**Implementation:**
- FastAPI app with CORS middleware
- Pydantic models for request/response
- SQLAlchemy for database ORM
- Async endpoints for LLM calls

---

## 10. Deployment: Minimal-First, AWS-Ready

**Decision:** Support both "minimal/low-cost" and "full AWS scale" deployment modes.

**Context:** MVP needs to ship fast with low ops; growth needs scalable infra.

**Alternatives:**
- AWS-only (expensive for MVP)
- Minimal-only (no scale path)
- Kubernetes everywhere (overengineered)

**Rationale:**
- Minimal mode: Vercel (web) + Fly.io (API) + Supabase (DB) → ship in hours, <$50/month
- Full AWS: ECS Fargate + Aurora + SQS → handles spikes, enterprise-ready
- Design for migration: Postgres-compatible DB, job abstraction (cron vs queue)

**Trade-offs:**
- Dual codepaths to maintain
- Need abstraction layers (storage, queue, scheduler)
- Terraform configs for both modes

**Implementation:**
- Minimal: GitHub Actions cron for jobs, Supabase Storage
- AWS: EventBridge scheduler, SQS, S3 + CloudFront
- Abstraction: `StorageAdapter`, `QueueAdapter`, `SchedulerAdapter`

---

## 11. RBAC for Admin Control Plane

**Decision:** Role-based access control with 4 roles: Owner, Admin, Coach, User.

**Context:** Multi-user deployments need permission boundaries.

**Alternatives:**
- No RBAC (everyone is admin)
- ACLs per resource
- Attribute-based access control (ABAC)

**Rationale:**
- Simple role model covers 95% of use cases
- Owner = full access including secrets/billing
- Admin = user management, no secrets
- Coach = can interact with programs, no policies
- User = self only
- Server-side enforcement prevents escalation

**Trade-offs:**
- Less flexible than ABAC
- Role explosion risk if over-complicated
- Need audit log for accountability

**Implementation:**
- Table: `users(id, email, role)`
- Decorator: `@requires_role("admin")` on endpoints
- Audit log: immutable table recording who/what/when
- Secrets never exposed to non-owner roles

---

**Status:** v0.1.0 - Core architecture decisions documented

**Next:** Complete MVP implementation based on these decisions
