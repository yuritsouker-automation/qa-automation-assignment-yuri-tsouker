# Design Rationale

## 1) Language and framework choice

This project uses Python + pytest + Playwright for UI, and `requests` + pytest for API.

- **Why Python/pytest: Fast to write, readable tests, rich fixture model, and a strong ecosystem (xdist, allure, parametrize). Most importantly, all products at Modelyo are written in Python — keeping the automation framework in the same language eliminates context switching, makes collaboration with developers significantly easier, and demonstrates my ability to design and build a production-ready automation framework from scratch in Python when the business requires it.
- **Why Playwright for UI:** better default auto-wait behavior, first-class modern browser support, stable locators, and cleaner debugging ergonomics for dynamic apps.
- **Why not Selenium here:** Selenium is mature and still valid, but usually needs more explicit synchronization and framework glue to reach the same reliability level.

**When I would pick Selenium instead:**
- Existing org-wide Selenium grid/tooling and deep in-house Selenium expertise.
- Legacy browsers/platforms where Selenium stack is already hardened.
- Large enterprise environment with reusable Selenium libraries already amortized.

## 2) Anti-flakiness strategy

Concrete techniques used in this repo:

- **Page Object Model** (`pages/*`) to centralize selectors and actions.
- **State-based waits** (`wait_for_page_load`, element visibility waits) instead of arbitrary sleeps.
- **Data-driven tests** from `test_data/*.json` to avoid inline magic values.
- **Fixture-based setup/teardown** (`tests/ui_tests/conftest.py`) for consistent login and cleanup.
- **Per-test cleanup** in cart flows to avoid state leakage across cases.
- **Explicit assertions with clear failure messages** for quick diagnostics.

What I would add at 1000+ tests:

- Retry policy only for known transient infrastructure errors (not assertion retries by default).
- Test impact analysis and smarter test selection per PR.
- Flaky-test quarantine workflow with SLA and owner.
- Contract/schema validation layer for APIs (JSON Schema / pydantic models).
- More deterministic test data lifecycle (seeded data and isolated tenant/account strategy).

## 3) Parallelism and isolation

Current parallelism is via `pytest-xdist` (`-n 3`) in local and CI.

Isolation model:

- Tests do not share mutable in-memory state.
- UI flows isolate by logging in per test and logging out/cleaning up afterward.
- API tests target JSONPlaceholder simulated writes; assertions validate response shape, not persistence.

What breaks first as parallelism increases:

- Shared-account collisions in UI (cart/session side effects).
- Environment throttling / rate limits.
- Slow setup phases (browser/bootstrap) becoming bottlenecks.

Mitigations:

- Separate test users per worker where needed.
- Tag and split suites (smoke/regression/api/ui) for predictable execution.
- Keep tests independent and idempotent; avoid order coupling.

## 4) Reporting and triage

In CI, on failure, on-call gets:

- GitHub Actions job logs (failed test names, stack traces, command output).
- Allure artifact (`reports/allure-report`) with test history, steps, and failure details.

Path to root cause at 3am:

1. Open failed workflow run and identify failing test node.
2. Open Allure artifact and inspect failed test details + assertion message.
3. Re-run the same test locally with the same browser/flags.
4. Check page-object locator/action in `pages/*` and fixture setup in `conftest.py`.
5. Classify: product regression vs locator drift vs data/env instability.
6. Apply targeted fix and keep regression test stable.

## 5) What I would do next (next 2 days)

Highest-value next step: **stabilization + observability hardening**.

- Add richer failure artifacts for UI (trace/video/screenshot on failure) and attach to CI artifacts.
- Add marker-based test taxonomy (`smoke`, `regression`, `api`, `ui`) plus CI matrix strategy.
- Add API schema helpers and reusable assertions to reduce duplication.
- Introduce environment-configurable base URLs for UI pages (remove hardcoded UI URLs from page objects).

Why this next: it improves signal quality, reduces time-to-diagnosis, and makes the suite scale safely before just adding more test count.

