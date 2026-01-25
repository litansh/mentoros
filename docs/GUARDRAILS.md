# docs/GUARDRAILS.md
MentorOS Guardrails (Behavioral + Technical)
Version: 1.0

This document defines the guardrails that ensure MentorOS behaves like a real coach, remains trustworthy, and operates safely at scale.

---

## 1) Trust & Accuracy Guardrails
1) No hallucinated links.
   - Every external URL must be verified before being sent.
2) No hallucinated certifications.
   - Certification references must link to official objectives pages where possible.
3) No invented prices.
   - If a price is unknown, label it as unknown and request verification or use “estimated” only with a source.
4) Always present tradeoffs.
   - If user prioritizes certificate prestige, acknowledge time/cost impact and offer alternatives.

---

## 2) Coaching Behavior Guardrails (Must feel like real mentorship)
1) Ask one question at a time during onboarding (no overwhelming forms).
2) Use “reflect + clarify + propose” loop:
   - Reflect user intent briefly
   - Clarify missing constraint
   - Propose next step
3) Maintain continuity:
   - Always reference the active goal and current week.
4) Be proactive but bounded:
   - reminders and follow-ups respect cadence policies and quiet hours.
5) Adaptation must be reasoned:
   - any plan change includes “why” + “what changed”.
6) Never guilt the user for stalling.
   - offer lighter mode or reschedule.

---

## 3) Safety & Privacy Guardrails
1) Never request:
   - passwords, tokens, OTP, private keys, employee secrets.
2) PII minimization:
   - store only what is needed (email/telegram_id + learning data).
3) Secure secrets:
   - store provider keys in secret manager / env, never in client.
4) Data export control:
   - user can export their own data.
   - admin can export user data only with owner permission.

---

## 4) Cost Guardrails
1) Enforce token caps per user (daily/weekly).
2) Model routing:
   - cheap model for reminders/check-ins, strong model for planning/complex feedback.
3) Avoid repeated plan regeneration:
   - regeneration only on user request or adaptation trigger.
4) Use caching for recurring explanations.
5) Batch weekly summaries (worker job).

---

## 5) Channel Guardrails
1) Messaging is not the primary learning surface.
   - send nudges, check-ins, small drills; deep content in Web.
2) Respect quiet hours and max messages/day.
3) Provide “unsubscribe/pause” in every channel.
4) WhatsApp channel:
   - use templates if required by provider
   - handle rate limits gracefully

---

## 6) Plan Quality Guardrails
1) Every plan must include:
   - goal statement
   - constraints summary
   - weekly schedule
   - tasks + estimated minutes
   - assessments cadence
   - success criteria
2) Every plan must state:
   - what will be achieved by week 2, week 4, week 8 (milestones)
3) Certification-first plans must include:
   - prerequisites
   - objectives link
   - practice exam schedule
   - readiness criteria

---

## 7) Failure Modes & Recovery
- Link verification fails:
  - replace with fallback resources
  - or send plan without links + request user preference
- LLM quota exceeded:
  - degrade to cheap model
  - delay deep analysis until next budget window
- Job failures:
  - retries with backoff
  - alert admin dashboard
- External provider (Telegram/WhatsApp/Notion) outage:
  - switch to email fallback where configured

---

## 8) Observability Guardrails
- Log every state transition with correlation_id
- Store an immutable audit log for admin actions
- Metrics:
  - active users
  - reminder success rate
  - link verification fail rate
  - avg tokens/user/day
  - stall rate
  - completion rate
- Alerting thresholds:
  - high failure rates on messaging sends
  - high verification failures
  - sudden token burn spikes

---
