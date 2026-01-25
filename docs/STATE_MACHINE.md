# docs/STATE_MACHINE.md
MentorOS State Machine (Closed Spec)
Version: 1.0

This document defines the exact user lifecycle, transitions, triggers, and side-effects.
It is intended to remove ambiguity for code-generation agents and ensure the system behaves like a real coach, not a chat toy.

---

## 1) Core Principles
- The system is **goal-first**. A goal must exist before a program exists.
- A program must be **explicitly approved** by the user before it becomes ACTIVE.
- The coach must be **proactive** (follow-ups) but never spammy (policy-controlled cadence).
- The system must be **adaptive**: it changes plan difficulty and pacing based on signals.
- All external resources must be **verified** before being sent.

---

## 2) States

### S0: START
Entry:
- Create User record (if new) and initialize session context.

Exit condition:
- User begins onboarding.

Transitions:
- START -> DISCOVERY

---

### S1: DISCOVERY (Onboarding Interview)
Goal:
- Collect structured onboarding answers in a coaching style (one-by-one questions).

Data captured (minimum):
- goal_title
- goal_context (why now)
- current_level (role, background)
- deadline (optional)
- time_per_week
- budget_cap_monthly
- flexibility constraints (schedule variability)
- learning style preference
- certification preference mode (skill-first/cert-assisted/cert-first)
- channel preferences (web/telegram/whatsapp/email)
- reminder cadence preference

Exit condition:
- Required fields captured and validated.

Transitions:
- DISCOVERY -> PLAN_DRAFT

Side effects:
- Persist onboarding answers incrementally after each question.
- Summarize onboarding context for long-term memory.

---

### S2: PLAN_DRAFT
Goal:
- Generate a structured plan (syllabus + schedule + tasks + assessments) under constraints.

Inputs:
- onboarding profile
- applicable policies (budget/token/provider/cert/channel)

Outputs:
- Program draft (JSON): weeks/modules/tasks
- Cost summary (estimated paid resources cost + LLM cost estimate)
- Time summary (estimated minutes/week)
- Links list (unverified initially; must be passed to verifier)

Transitions:
- PLAN_DRAFT -> VERIFICATION_QUEUE (internal) -> PLAN_REVIEW

Side effects:
- Create Program status=draft
- Enqueue verification tasks for all URLs

---

### S3: PLAN_REVIEW
Goal:
- Present the plan to the user, allow edits, require explicit approval.

User actions:
- Approve
- Request edits (change load, topics, deadline, certification preference)
- Cancel

Transitions:
- PLAN_REVIEW -> APPROVED (if user approves)
- PLAN_REVIEW -> PLAN_DRAFT (if edits requested)
- PLAN_REVIEW -> START (if canceled)

Invariants:
- No activation without explicit approval.

Side effects:
- If edits requested: log diff request; regenerate plan
- If approved: store approved_at timestamp; freeze v1 baseline of syllabus

---

### S4: APPROVED
Goal:
- Prepare execution: schedule tasks, set reminders, initialize module 1.

Transitions:
- APPROVED -> ACTIVE

Side effects:
- Generate first module messages
- Schedule reminder jobs (based on cadence policy)
- Initialize progress metrics

---

### S5: ACTIVE (Execution + Coaching)
Goal:
- Deliver tasks, coach Q&A, run check-ins, track progress.

Inputs:
- user interactions (Q&A, completion, reschedule)
- scheduled events (reminders, weekly summary, assessment triggers)
- policy constraints (budgets/token caps)

Transitions:
- ACTIVE -> ASSESS (end of module or triggered)
- ACTIVE -> STALLED (if stall conditions met)
- ACTIVE -> PAUSED (admin/user pause)
- ACTIVE -> COMPLETE (if completion threshold met)

Side effects:
- Update Task statuses
- Generate coaching feedback on demand
- Maintain “weekly plan” message cadence

---

### S6: ASSESS
Goal:
- Run module-level quiz + scenario drill.

Assessment types:
- Quiz (5–10 Q)
- Scenario (board-style or goal-style open response)

Scoring:
- numeric score + qualitative feedback
- identify gaps by topic tags

Transitions:
- ASSESS -> ADAPT (always after assessment)
- ASSESS -> ACTIVE (if adaptation not needed; still store results)

Side effects:
- Persist assessment results
- Add remediation tasks if needed
- Update readiness score

---

### S7: ADAPT
Goal:
- Adjust plan based on performance, capacity, and stalling signals.

Adaptation actions:
- reduce or increase weekly load
- reorder modules
- add remediation
- change drill difficulty
- recommend certification track shift (only with user approval if cost changes)

Transitions:
- ADAPT -> ACTIVE

Side effects:
- Create a new program revision (v2, v3...) with change log
- Notify user of changes and reason
- If significant change: ask for confirmation (soft gate)

---

### S8: STALLED
Goal:
- Recover the user without guilt. Offer lighter plan or rescheduling.

Triggers:
- No task completion for N days
- Reminders ignored N times
- User explicitly says “too busy/stuck”

Recovery options:
- “Light week” mode
- “Reset cadence” (new schedule)
- “Micro-steps only”
- “Pause program”

Transitions:
- STALLED -> ACTIVE (recovered)
- STALLED -> PAUSED (paused)
- STALLED -> PLAN_REVIEW (major replan)

Side effects:
- Log stall event
- Update plan if needed

---

### S9: PAUSED
Goal:
- Stop reminders and tasks until resumed.

Transitions:
- PAUSED -> ACTIVE (resume)
- PAUSED -> COMPLETE (if user cancels permanently)

Side effects:
- Disable reminder jobs
- Keep state intact

---

### S10: COMPLETE
Goal:
- Produce final report, exports, optional internal certificate.

Completion criteria (configurable):
- X% tasks completed
- final assessment score >= threshold (optional)
- user confirms completion

Transitions:
- COMPLETE -> START (new goal/program)

Side effects:
- Generate final PDF report
- Export Notion program summary (if enabled)
- Generate internal certificate (if enabled)
- Suggest next goal or continuation path

---

## 3) Events (Normalized)
- USER_MESSAGE
- USER_TASK_COMPLETE
- USER_RESCHEDULE_REQUEST
- USER_PLAN_APPROVE
- USER_PLAN_EDIT_REQUEST
- JOB_REMINDER_TICK
- JOB_WEEKLY_SUMMARY_TICK
- JOB_ASSESSMENT_TRIGGER
- ADMIN_PAUSE/RESUME/DISABLE
- POLICY_UPDATE

---

## 4) Stall & Adaptation Defaults (Policies)
- stall_days_without_completion: 7
- stall_ignored_reminders: 2
- assessment_frequency: end_of_module
- remediation_threshold_score: 70
- hard_fail_threshold_score: 50 (force remediation module)

---
