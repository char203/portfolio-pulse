# Portfolio Pulse — Streamlit

## Run locally

From the `portfolio-pulse` project root:

```bash
python3 -m pip install -r requirements_streamlit.txt
streamlit run app.py
```

If `streamlit` is not on your PATH:

```bash
python3 -m streamlit run app.py
```

## Expected project files

The app expects these existing modules in the same project root:

- `market_engine.py`
- `analytics.py`
- `data.py`
- `portfolio.py`
- `scenarios.py`
- `attribution.py`
- `sensitivity.py`

This Streamlit app is deliberately a thin presentation layer. The validated Python finance engine remains the source of truth.
