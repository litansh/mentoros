# MentorOS

**AI-powered goal-to-mastery learning platform with personalized coaching, structured programs, and accountability.**

Build custom learning paths from goals to mastery with multi-agent orchestration, resource verification, and adaptive coaching that keeps learners on track.

---

## 🎯 Why It Exists

**Problem:** Generic online courses and chatbots don't provide structured paths from "I want to learn X" to "I've mastered X." Learners struggle with:
- Vague goals without concrete plans
- Unverified or unreliable learning resources
- No accountability or adaptation when stuck
- Information overload without curation

**Solution:** MentorOS turns goals into structured, approved programs with:
- Multi-agent system (Architect, Mentor, Coach, Verifier)
- Curated resource registry with link verification
- Human-in-the-loop approval gates
- Adaptive coaching with stall detection
- Cost governance and budget controls

---

## 🚀 What It Does

### Core Capabilities

- **Goal Onboarding:** Structured discovery to understand learner's goal, constraints, time availability, budget, and certification preferences
- **Custom Program Generation:** AI Learning Architect creates personalized syllabus with modules, tasks, pacing, and workload estimates
- **Approval-Gated Plans:** No program becomes active without explicit learner approval
- **Resource Verification:** All external links verified before sending (14-day cache TTL)
- **Execution Coaching:** Weekly check-ins, nudges, stall detection, and recovery tactics
- **Assessments & Adaptation:** Quizzes, scenario grading, and program adaptation based on results
- **Multi-Channel Delivery:** Web UI (primary) + Telegram/WhatsApp/Email (accountability)
- **Exports:** Notion sync, PDF reports, and completion certificates
- **Admin Control Plane:** RBAC, cost governance, policy enforcement, audit logs

### Multi-Agent Architecture

1. **Learning Architect** - Goal → structured syllabus with dependencies, pacing, workload estimates
2. **Subject Mentor** - Answers questions, creates examples, provides context-aware teaching
3. **Coach** - Weekly check-ins, accountability nudges, stall detection, reflection prompts
4. **Verifier/Guardrails** - Validates links, enforces budgets/policies, blocks hallucinations

---

## 🏗️ Architecture

### High-Level Components

```
┌────────────────────────────────────────────────────┐
│  Channels (Multi-Channel Interface)                │
│  ├─ Web UI (Next.js) - Primary                    │
│  ├─ Telegram Bot - Reminders/Check-ins            │
│  ├─ WhatsApp (Twilio/Meta) - Optional             │
│  └─ Email - Fallback                              │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│  Core API (FastAPI)                                │
│  ├─ State Machine (9 states: Discovery → Active)  │
│  ├─ Multi-Agent Orchestrator                      │
│  ├─ Curriculum Engine                             │
│  ├─ Assessment Engine                             │
│  ├─ Verification Engine                           │
│  ├─ Admin APIs (RBAC + Audit)                     │
│  └─ Export Generators (Notion/PDF)                │
└────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────┐
│  Data Layer                                        │
│  ├─ PostgreSQL - Users, Programs, Tasks, Policies │
│  ├─ Redis - Job queue, rate limiting (optional)   │
│  ├─ Object Storage - PDFs, certificates           │
│  └─ Resource Registry (YAML) - Curated sources    │
└────────────────────────────────────────────────────┘
```

### State Machine (Program Lifecycle)

```
START → DISCOVERY → PLAN_DRAFT → PLAN_REVIEW → APPROVED
        ↓
      ACTIVE ⇄ ASSESS ⇄ ADAPT
        ↓
     COMPLETE
```

**Key Invariants:**
- No program becomes ACTIVE without explicit approval
- No external link sent unless verified (or from registry with valid TTL)
- Paid resources/certifications require explicit opt-in
- Budget and token caps enforced per user/program/timewindow

---

## 🏃 Quickstart

### Prerequisites

- Python 3.10+
- PostgreSQL (or use Supabase/Neon)
- OpenAI API key (or Anthropic)

### Local Setup (~5 minutes)

```bash
git clone https://github.com/litansh/mentoros.git
cd mentoros

# Setup environment
cp .env.example .env
# Edit .env: Add OPENAI_API_KEY and DATABASE_URL

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Load resource registry
python scripts/load_registry.py resources/registry.yaml

# Start API
cd backend
uvicorn main:app --reload --port 8000
```

**Access:**
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Demo Flow (Test Core Features)

```bash
# 1. Create a test user
curl -X POST http://localhost:8000/api/onboarding/start \
  -H "Content-Type: application/json" \
  -d '{"goal": "Learn Python for data science", "hours_per_week": 5}'

# 2. Generate learning plan
curl -X POST http://localhost:8000/api/plan/generate

# 3. View generated program
curl http://localhost:8000/api/program/current

# 4. Simulate plan approval
curl -X POST http://localhost:8000/api/plan/approve

# 5. Complete first task
curl -X POST http://localhost:8000/api/task/complete \
  -d '{"task_id": "<TASK_ID>"}'
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# ===== REQUIRED =====
# OpenAI or Anthropic
OPENAI_API_KEY=sk-xxx
# OR
ANTHROPIC_API_KEY=sk-ant-xxx

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/mentoros

# ===== OPTIONAL - Channels =====
# Telegram (easiest for reminders/check-ins)
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_WEBHOOK_SECRET=your_secret

# WhatsApp via Twilio (optional)
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_WHATSAPP_NUMBER=+14155238886

# Email (fallback)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=app_password

# ===== OPTIONAL - Admin =====
ADMIN_EMAIL=admin@example.com  # Owner role
SECRET_KEY=your_secret_key_for_sessions

# ===== OPTIONAL - Cost Governance =====
DAILY_TOKEN_CAP=100000
MONTHLY_BUDGET_USD=50
MODEL_ROUTING=smart  # smart|cheap|premium

# ===== OPTIONAL - Exports =====
NOTION_API_KEY=secret_xxx  # For Notion sync
```

### Resource Registry

Edit `resources/registry.yaml` to add curated learning resources:

```yaml
resources:
  - title: "Python Official Tutorial"
    url: "https://docs.python.org/3/tutorial/"
    provider: "python.org"
    topics: ["python", "basics"]
    cost_type: "free"
    cert_relevance: "none"
    trust_score: 0.95
    verified_at: "2026-02-01"
```

---

## 📊 Observability

### Logs

```bash
# Structured JSON logs
tail -f logs/mentoros.log | jq

# Key events:
# - "program_created", "plan_approved", "task_completed"
# - "assessment_scored", "stall_detected", "adaptation_triggered"
# - "verification_failed", "policy_violation", "admin_action"
```

### Metrics (Future)

- Program completion rate
- Average time to mastery
- Stall detection accuracy
- Resource verification success rate
- Cost per user per month

### Admin Dashboard

```bash
# Access admin UI
open http://localhost:3000/admin

# View:
# - Active users and their program status
# - Cost burn rate and top drivers
# - Policy violations
# - Audit log
```

---

## 🗺️ Roadmap

### ✅ Phase 1: MVP Foundation (Current)
- [x] Core state machine (9 states)
- [x] Multi-agent orchestration (4 agents)
- [x] Resource registry + link verification
- [x] Policy engine + cost governance
- [x] FastAPI backend skeleton
- [x] Comprehensive spec (docs/SPEC.md)

### 🔄 Phase 2: Complete MVP (In Progress)
- [ ] Web UI (Next.js) - onboarding, plan approval, task dashboard
- [ ] Telegram bot integration
- [ ] Assessment engine + scoring
- [ ] Adaptation logic (stall detection + recovery)
- [ ] Admin portal (RBAC + audit logs)
- [ ] Notion export
- [ ] Database schema + migrations

### 📋 Phase 3: Production Hardening (Q2 2026)
- [ ] Email channel adapter
- [ ] PDF export + certificates
- [ ] Job scheduler (reminders, summaries)
- [ ] Full test coverage
- [ ] Rate limiting + caching
- [ ] Monitoring + alerting
- [ ] Cost optimization (model routing)

### 🚀 Phase 4: Scale & Premium Features (Q3 2026)
- [ ] WhatsApp adapter (Twilio/Meta)
- [ ] Multi-tenant architecture
- [ ] Certification-first mode with exam prep
- [ ] Advanced coaching (reflection prompts, scenario-based learning)
- [ ] Full AWS deployment (ECS Fargate + Aurora)
- [ ] Self-serve admin onboarding

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

Copyright (c) 2026 Litan Shamir

---

## ⚠️ Disclaimer

**Development Status:** MVP in progress. Core architecture complete, full features under active development.

**Recommended Use:**
- Test in development environment first
- Resource registry requires manual curation for your domain
- Cost governance policies should be configured before production use
- Admin RBAC must be properly configured for multi-user deployments

**Security:**
- Never commit `.env` files with real credentials
- Use secrets management (AWS Secrets Manager, HashiCorp Vault) in production
- Review all admin actions in audit logs
- Rotate API keys quarterly

**Cost Awareness:**
- LLM costs are primary variable (~$20-50/user/month depending on usage)
- Set DAILY_TOKEN_CAP and MONTHLY_BUDGET_USD in .env
- Monitor cost dashboard in admin UI
- Start with cheap models, upgrade to smart routing after validation

---

## 📚 Documentation

- **[SPEC.md](docs/SPEC.md)** - Complete architecture specification (410 lines)
- **[STATE_MACHINE.md](docs/STATE_MACHINE.md)** - Program lifecycle state transitions
- **[AGENT_PROMPTS.md](docs/AGENT_PROMPTS.md)** - Multi-agent prompt templates
- **[GUARDRAILS.md](docs/GUARDRAILS.md)** - Verification rules and policy enforcement
- **[POLICY_SCHEMA.md](docs/POLICY_SCHEMA.md)** - Cost governance and RBAC configuration

---

**Status:** 🔄 MVP in active development | Core architecture complete (~600 lines Python)

**Target:** Goal-to-mastery learning platform with <$50/user/month operating cost
