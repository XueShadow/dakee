# CS 315 - Application Development and Emerging Technologies

## Activity 3: AI MovieLens

AI MovieLens is a GenAI-powered Streamlit application for exploring movie data and analyzing movie-related text. It combines the MovieLens small dataset with a Hugging Face language model to produce an executive summary, themes, characters, relationships, emotions, conflicts, scenes, and evidence-based insights.

## 1. App Idea

The app's purpose is to help students study narrative patterns in movies. A user can select a movie from the MovieLens catalog, paste a synopsis or scene description, or upload a text, PDF, or Word document. The application then analyzes the supplied material and separates source evidence from interpretation.

The selected dataset is the [MovieLens latest-small dataset](data/ml-latest-small/), which includes:

- `movies.csv`: movie titles and genres
- `ratings.csv`: user ratings
- `tags.csv`: community-generated tags
- `links.csv`: IMDb and TMDb identifiers

## 2. Project Structure

```text
AI MovieLens/
├── data/ml-latest-small/       # MovieLens dataset
├── backend/app/                # Optional FastAPI API surface
├── backend/tests/              # API regression tests
├── streamlit_app.py            # Complete single-file Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md
```

The deployed Streamlit application is intentionally self-contained in `streamlit_app.py`. It includes the interface, MovieLens loading and cleaning, text extraction, validation, local fallback analysis, Hugging Face integration, and result formatting in one file.

## 3. Environment Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Add a Hugging Face access token to `.env` to enable model-generated analysis:

```env
HUGGINGFACE_API_KEY=your_token_here
HUGGINGFACE_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

Never commit `.env` or expose the token in source code. If no token is configured, the app uses its local evidence-based fallback and labels the result clearly.

## 4. Dataset Loading and Cleaning

The app loads the MovieLens CSV files with Pandas in `streamlit_app.py`. During loading it:

- Combines movie titles with ratings, tags, and external links.
- Calculates average ratings and rating counts per movie.
- Removes blank titles, missing genres, and entries marked `(no genres listed)`.
- Normalizes whitespace and removes duplicate titles.
- Converts identifiers and rating counts into display-safe values.
- Sorts the catalog alphabetically for the sidebar selector.

## 5. GenAI Analysis

When a Hugging Face token is configured, the app sends the supplied movie text to the Hugging Face chat-completions endpoint. The model is instructed to return structured JSON containing:

- Executive summary
- Themes and supporting evidence
- Characters and development
- Relationships and sources of tension
- Conflicts and emotional impact
- Emotions and important scenes
- Relational dialectics
- Evidence-based insights

The app validates the response before displaying it. If the API rejects a request, the interface shows the provider's error instead of silently presenting a local result as AI-generated.

## 6. Streamlit Interface

The interface provides interactive widgets for:

- Selecting a MovieLens title
- Loading a blank analysis template
- Uploading `.txt`, `.pdf`, and `.docx` files
- Pasting or editing source text
- Starting an analysis
- Clearing the workspace
- Asking questions about the completed analysis

The report is organized into tabs for the overview, themes, characters, relationships, conflicts, emotions, scenes, dialectics, and Q&A.

## 7. Visualization

The application uses Streamlit charts to visualize the analysis:

- Theme distribution is displayed as a bar chart.
- Emotion frequency is displayed as a grouped bar chart.
- Metric cards show the number of detected characters, themes, conflicts, and scenes.

## 8. Testing and Iteration

Run the API tests with:

```bash
pytest backend/tests/test_api.py -q
```

The tests cover the health endpoint, empty-input validation, response structure, Hugging Face error handling, and MovieLens metadata extraction. The app can also be smoke-tested with:

```bash
streamlit run streamlit_app.py
```

Then open the local URL shown by Streamlit, select a movie or upload text, and click **Analyze narrative**.

## 9. Deployment to Streamlit Community Cloud

1. Push the project to a GitHub repository.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select the repository and set the main file to `streamlit_app.py`.
4. Add `HUGGINGFACE_API_KEY` and `HUGGINGFACE_MODEL` under the app's Secrets settings.
5. Deploy and test the public app URL.

The API key must be added through Streamlit Secrets, not committed to the repository.

## 10. Next Goals

- Add filters for genres, rating ranges, and movie release periods.
- Add a chatbot that can answer follow-up questions about the selected dataset and analysis.
- Add comparison views for multiple movies.
- Add export options for reports and charts.
- Expand evaluation tests for prompt quality, response validity, and unsupported model errors.

## Security and Limitations

- Secrets are loaded from environment variables and are not displayed in the interface.
- Uploaded files are processed in the session; when Hugging Face is configured, submitted text is sent to its inference API.
- Uploaded files are not permanently stored by default.
- The result is an academic analysis aid, not a definitive interpretation of a movie.
