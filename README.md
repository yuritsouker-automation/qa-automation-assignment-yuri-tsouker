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

### 3) Open HTML report

```zsh
open reports/report.html
```

Playwright traces/videos/screenshots are also saved in `reports/playwright-report`.


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

- Playwright artifacts from `reports/playwright-report`
- Pytest HTML report from `reports/report.html`

