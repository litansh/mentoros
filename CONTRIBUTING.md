# Contributing to MentorOS

Thank you for your interest in contributing to MentorOS!

## Development Setup

```bash
# Clone repository
git clone https://github.com/litansh/mentoros.git
cd mentoros

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Testing and linting tools

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python scripts/init_db.py

# Run tests
pytest

# Start dev server
cd backend
uvicorn main:app --reload
```

## Development Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test locally**
   ```bash
   pytest                          # Run tests
   black backend/ tests/          # Format code
   isort backend/ tests/          # Sort imports
   flake8 backend/ tests/         # Lint
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- **Python:** Follow PEP 8, use Black formatter
- **Line length:** 120 characters
- **Imports:** Use isort for consistent import ordering
- **Type hints:** Use where applicable
- **Docstrings:** Google style for functions and classes

## Testing

- Write tests for all new features
- Maintain >80% code coverage
- Use pytest fixtures for common setups
- Mock external services (OpenAI, Telegram, etc.)

## Architecture

- See `docs/SPEC.md` for complete architecture
- Follow existing patterns for agents, state machine, policies
- Keep agents focused and single-purpose
- All external links must go through verification engine

## Pull Request Guidelines

- **Title:** Use conventional commits (feat:, fix:, docs:, refactor:, test:)
- **Description:** Explain what, why, and how
- **Tests:** Include test coverage
- **Documentation:** Update relevant docs
- **Breaking changes:** Clearly document in PR description

## Security

- Never commit credentials or API keys
- Use `.env` files (never committed)
- Review all agent prompts for potential prompt injection
- Validate all user inputs
- Follow principle of least privilege for RBAC

## Questions?

- Open an issue for bugs or feature requests
- Check `docs/` for architecture and design decisions
- See existing code for patterns and conventions
