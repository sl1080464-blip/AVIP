# Contributing to AVIP

## Environment setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

## Git workflow

- create a branch using a clear feature name
- keep commits small and focused
- use conventional prefixes such as `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`
- open a pull request with a concise description and acceptance criteria

## Code standards

- prefer small, well-named modules
- add type hints to public functions and services
- keep business logic separate from the API layer
- document architectural decisions in the `docs/` tree

## Testing

```bash
pytest backend/tests
ruff check backend
mypy backend
```

## Pull request checklist

- tests pass
- docs updated if behavior or architecture changed
- no secrets or `.env` files committed
- API changes include a short example or description
