# AI Algorithm Explainer

A Streamlit learning tool that uses Hugging Face Inference Providers to explain algorithms and code. It describes the core idea, walks through the supplied logic, analyzes time and space complexity, and highlights correctness assumptions and edge cases.

The app does not execute submitted code and does not generate a local fallback explanation. A Hugging Face token with Inference Providers permission is required.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `HUGGINGFACE_API_KEY` in `.env` to your Hugging Face user access token with permission to make calls to Inference Providers. The default model is `meta-llama/Llama-3.1-8B-Instruct`; override it with `HUGGINGFACE_MODEL` if needed. The model is configured through `.env`, not the app UI.

## Run

```bash
streamlit run app.py
```

Streamlit prints the local URL, usually `http://localhost:8501`.

## Test

```bash
pytest -q
```

## AI Algorithm Explainer: Project Details

1. **App idea:** AI Algorithm Explainer is a computer science learning tool. It explains algorithms and code, including their purpose, core idea, steps, complexity, correctness assumptions, and edge cases. The accompanying dataset is the AI4I 2020 predictive maintenance dataset; the app currently displays it but does not train a machine-failure prediction model.

2. **Environment and project structure:** The app uses Python, Streamlit, Pandas, Hugging Face Hub, and python-dotenv. Its main files are `app.py` for the interface and dataset table, `explainer.py` for Hugging Face requests, `requirements.txt` for dependencies, `.env.example` for configuration, `tests/test_explainer.py` for tests, and `data/ai4i2020.csv` for the dataset.

3. **Dataset loading and cleaning:** `app.py` loads `data/ai4i2020.csv` with `pandas.read_csv`. It contains 10,000 rows and 14 columns, including product type, operating measurements, machine-failure labels, and failure-mode indicators. The app displays the data as supplied and does not currently transform or clean its rows.

4. **GenAI integration:** `explainer.py` uses Hugging Face Inference Providers through `InferenceClient` with automatic provider selection. The model explains the user-selected algorithm or pasted code; dataset analysis is not currently sent to the model. Set `HUGGINGFACE_API_KEY` in `.env` or deployment secrets. No local AI fallback is used.

5. **Streamlit interface:** Users can select from 50 examples across nine algorithm families, load an example into the editor, paste or edit code, request an explanation, and clear the workspace. The dataset table is displayed below the explainer.

6. **Visualization:** The dataset view uses an interactive Streamlit dataframe and summary metrics for record count, feature count, and machine-failure count and rate. Charts and dataset filters have not been implemented yet.

7. **Testing and iteration:** Run `pytest -q`. The four tests cover automatic Hugging Face provider selection, missing API credentials, empty input, and provider errors. The algorithm examples are also checked for syntax and dropdown loading.

8. **Deployment:** Deploy `app.py` to Streamlit Community Cloud, install dependencies from `requirements.txt`, and set `HUGGINGFACE_API_KEY` in the app's Secrets settings. Keep `.env` private. Include `data/ai4i2020.csv` in the deployed repository so the dataset table can load.

9. **Next goals:** Add filters by product type and failure mode, charts for failure rates and operating measurements, and dataset-aware GenAI analysis grounded in selected rows. A chatbot could answer questions about the dataset using retrieved records as context.
