# Changelog

All notable changes to MentorOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned (MVP Completion)
- Web UI (Next.js) for onboarding, plan approval, task dashboard
- Telegram bot integration
- Assessment engine with scoring and feedback
- Adaptation logic (stall detection + recovery)
- Admin portal (RBAC + audit logs)
- Notion export
- Database migrations
- Email channel adapter
- PDF export + certificates

## [0.1.0] - 2026-02-17

### Added
- **Core Architecture** (~600 lines Python)
  - State machine with 9 states (START → COMPLETE)
  - Multi-agent orchestration (Learning Architect, Mentor, Coach, Verifier)
  - Policy engine with cost governance
  - Resource registry + link verification engine

- **Backend Implementation**
  - FastAPI application skeleton
  - Data models (User, Goal, Program, Module, Task, Policy)
  - State management and transitions
  - Agent prompts (planner, coach)
  - LLM interface abstraction (OpenAI/Anthropic)
  - Verification engine (link validation with TTL caching)

- **Documentation**
  - Complete architecture specification (docs/SPEC.md - 410 lines)
  - State machine documentation (docs/STATE_MACHINE.md)
  - Agent prompts reference (docs/AGENT_PROMPTS.md)
  - Guardrails and verification rules (docs/GUARDRAILS.md)
  - Policy schema documentation (docs/POLICY_SCHEMA.md)

- **Project Infrastructure**
  - MIT License
  - .env.example with comprehensive configuration
  - .gitignore for Python projects
  - README.md (product-grade)
  - CONTRIBUTING.md
  - CHANGELOG.md
  - CODE_OF_CONDUCT.md

### Architecture Decisions
- Postgres for canonical state (users, programs, tasks, policies)
- FastAPI for API layer (performance + auto-docs)
- Multi-agent pattern with specialized prompts
- Approval-gated program lifecycle (human-in-the-loop)
- Resource registry YAML format for curation
- Link verification with 14-day TTL cache
- Cost governance via token budgets and model routing

### Core Invariants Implemented
- No program becomes ACTIVE without explicit approval
- No external link sent unless verified or from registry with valid TTL
- Paid resources/certifications require explicit opt-in
- Budget and token caps enforced per user/program/timewindow
- Admin actions are RBAC-protected and audited (planned)

## [0.0.1] - 2026-01-10

### Initial
- Project structure and repository setup
- Initial concept and specification

[Unreleased]: https://github.com/litansh/mentoros/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/litansh/mentoros/releases/tag/v0.1.0
[0.0.1]: https://github.com/litansh/mentoros/releases/tag/v0.0.1
