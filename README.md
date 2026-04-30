# QA Automation Assignment

UI and API automation suite using `pytest`, `playwright`, `requests`, and `pytest-xdist`.

## Run in Under 5 Minutes

### 1) Clone and install

```zsh
git clone <YOUR_REPO_URL>
cd qa-automation-assignment-yuri-tsouker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

### 2) Run all tests (UI + API) with 3 workers

```zsh
python -m pytest tests/ -n 3 --browser chromium -v
```

### 3) Open Playwright artifacts

```zsh
open reports/playwright-report
```

Playwright traces/videos/screenshots are saved in `reports/playwright-report`.
Screenshots and videos are retained only for failed tests.

---

## Failure Artifacts

On test failure, Playwright automatically captures:

| Artifact | File | How to open |
|---|---|---|
| Screenshot | `test-failed-1.png` | Any image viewer |
| Video | `video.webm` | Any media player |
| Trace | `trace.zip` | `python -m playwright show-trace <path>` |

Each failed test gets its own folder under `reports/playwright-report/`, named after the test node ID.

### View trace locally

```zsh
python -m playwright show-trace reports/playwright-report/<failed-test-folder>/trace.zip
```

### Example CI runs

**✅ All tests passing:**

🔗 [Example successful run — CI #25171629582](https://github.com/yuritsouker-automation/qa-automation-assignment-yuri-tsouker/actions/runs/25171629582)

**❌ Tests with failures (screenshot + video captured):**

🔗 [Example failed run — CI #25169556295](https://github.com/yuritsouker-automation/qa-automation-assignment-yuri-tsouker/actions/runs/25169556295)

Download the `playwright-report` artifact from the **Artifacts** section of a failed run to see:
- `test-failed-1.png` — screenshot at the moment of failure
- `video.webm` — full test session recording
- `trace.zip` — interactive Playwright trace viewer file

---

## Useful Commands

### UI tests only

```zsh
python -m pytest tests/ui_tests -n 3 --browser chromium -v
```

### API tests only

```zsh
python -m pytest tests/api_tests -n 3 -v
```

### Run headed (headless=false)

```zsh
python -m pytest tests/ui_tests --browser chromium --headed -v
```

### Clean old Playwright artifacts

```zsh
rm -rf reports/playwright-report/*
```

---

## Prerequisites

- Python 3.13 (CI uses 3.13)
- Chromium browser dependencies for Playwright (installed by `python -m playwright install --with-deps chromium`)

### Optional runtime overrides

You can override defaults from `pytest.ini` at runtime:

```zsh
python -m pytest tests/ui_tests --ui-base-url https://www.saucedemo.com -v
python -m pytest tests/api_tests --api-base-url https://jsonplaceholder.typicode.com --api-timeout 15 -v
```

Environment variables are also supported:

```zsh
export UI_BASE_URL=https://www.saucedemo.com
export API_BASE_URL=https://jsonplaceholder.typicode.com
python -m pytest tests/ -n 3 --browser chromium -v
```

---

## CI

GitHub Actions workflow is in `.github/workflows/ci.yml` and runs tests on:

- every branch push
- pull requests to `main`
- manual trigger (`workflow_dispatch`)

CI retains and uploads:

- Playwright artifacts from `reports/playwright-report` (screenshots, videos, traces for failed tests)
Test

