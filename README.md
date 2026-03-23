# can-i-run-ai-dashboard

Streamlit dashboard for the `canirunai` Python SDK.

## Local Run

This project targets Python 3.14 because the upstream `canirunai` package currently declares `requires-python >=3.14`.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e .
streamlit run app.py
```

## Container Run

```bash
docker build -t can-i-run-ai-dashboard:dev .
docker run --rm -p 8501:8501 can-i-run-ai-dashboard:dev
```
