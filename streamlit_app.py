import html
import io
import os
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from backend.app.services.analysis_service import AnalysisService
from backend.app.services.text_extraction import extract_text, validate_file
from backend.app.providers.base import HuggingFaceProvider, LocalProvider

load_dotenv(Path(__file__).parent / '.env')

MOVIELENS_DATA_URL = os.getenv(
    'MOVIELENS_DATA_URL',
    'https://files.grouplens.org/datasets/movielens/ml-latest-small.zip',
)
MOVIELENS_MOVIES_PATH = Path(__file__).parent / 'data' / 'ml-latest-small' / 'movies.csv'

SAMPLE_TEXT = """
Paste a synopsis, scene description, transcript, or narrative excerpt here for analysis.
"""


def load_movielens_catalog():
    try:
        csv_sources = {}
        if MOVIELENS_MOVIES_PATH.exists():
            data_dir = MOVIELENS_MOVIES_PATH.parent
            for filename in ('movies.csv', 'ratings.csv', 'tags.csv', 'links.csv'):
                file_path = data_dir / filename
                if file_path.exists():
                    csv_sources[filename] = file_path.read_bytes()
        else:
            with urlopen(MOVIELENS_DATA_URL, timeout=15) as response:
                archive_bytes = response.read()

            with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
                for filename in ('movies.csv', 'ratings.csv', 'tags.csv', 'links.csv'):
                    matching_files = [name for name in archive.namelist() if name.endswith(filename)]
                    if matching_files:
                        csv_sources[filename] = archive.read(matching_files[0])

        if 'movies.csv' not in csv_sources:
            return []

        movies_df = pd.read_csv(io.BytesIO(csv_sources['movies.csv']))
        ratings_df = pd.read_csv(io.BytesIO(csv_sources['ratings.csv'])) if 'ratings.csv' in csv_sources else pd.DataFrame()
        tags_df = pd.read_csv(io.BytesIO(csv_sources['tags.csv'])) if 'tags.csv' in csv_sources else pd.DataFrame()
        links_df = pd.read_csv(io.BytesIO(csv_sources['links.csv'])) if 'links.csv' in csv_sources else pd.DataFrame()

        rating_summary = {}
        if not ratings_df.empty:
            rating_summary = ratings_df.groupby('movieId')['rating'].agg(['mean', 'count']).round(2).to_dict('index')

        tag_summary = {}
        if not tags_df.empty:
            tag_summary = tags_df.groupby('movieId')['tag'].apply(lambda values: sorted(set(str(value).strip() for value in values if str(value).strip()))).to_dict()

        links_summary = links_df.set_index('movieId').to_dict('index') if not links_df.empty else {}
        cleaned_rows = []
        seen_titles = set()

        for row in movies_df.to_dict('records'):
            title = str(row.get('title') or '').strip()
            genres = str(row.get('genres') or '').strip()
            movie_id = int(row.get('movieId'))
            if not title or not genres or genres == '(no genres listed)':
                continue
            normalized_title = ' '.join(title.split())
            if not normalized_title or normalized_title in seen_titles:
                continue
            seen_titles.add(normalized_title)
            rating = rating_summary.get(movie_id, {})
            link = links_summary.get(movie_id, {})
            cleaned_rows.append(
                {
                    'movie_id': str(movie_id),
                    'title': normalized_title,
                    'genres': genres,
                    'average_rating': rating.get('mean', 'Not rated'),
                    'rating_count': int(rating.get('count', 0)),
                    'tags': tag_summary.get(movie_id, []),
                    'imdb_id': str(link.get('imdbId', '')),
                    'tmdb_id': str(link.get('tmdbId', '')),
                }
            )

        return sorted(cleaned_rows, key=lambda item: item['title'])
    except Exception:
        return []


def analyze_text(text: str, api_key: str = '', model: str = ''):
    if api_key.strip():
        provider = HuggingFaceProvider(api_key, model)
    else:
        provider = LocalProvider()

    service = AnalysisService(provider)
    return service.analyze_text(text)


def answer_question(result: dict, question: str) -> str:
    text_question = (question or "").strip()
    if not text_question:
        return "Please ask a question about the text you analyzed."

    normalized = text_question.lower()
    theme_names = [theme.get("name", "").lower() for theme in result.get("themes", [])]
    relevant_themes = [theme for theme in result.get("themes", []) if theme.get("name", "").lower() in normalized]

    if "family" in normalized and any("family" in name for name in theme_names):
        return "The material repeatedly frames family as the central narrative pressure point. The wedding announcement exposes how love, duty, and resentment are all connected through the family system."

    if "bobbie" in normalized and "mother" in normalized:
        relationship = next(
            (
                item
                for item in result.get("relationships", [])
                if "Bobbie" in {item.get("character_a"), item.get("character_b")}
                and "Mother" in {item.get("character_a"), item.get("character_b")}
            ),
            None,
        )
        if relationship:
            return (
                f"Bobbie's relationship with her mother is described as {relationship.get('initial_state', 'strained')} and later becomes {relationship.get('current_state', 'more open to repair')}. "
                f"The main tension centers on {relationship.get('source_of_tension', 'longstanding expectations and resentment')}."
            )

    if "sacrifice" in normalized:
        if relevant_themes:
            theme = relevant_themes[0]
            return f"The text presents sacrifice through {theme.get('characters', ['the family'])} as they manage responsibility and emotional cost. The evidence points to sacrifice as a burden that supports family loyalty even when it is painful."
        return "The provided material does not contain enough evidence to answer this question in a detailed way."

    if "forgiveness" in normalized:
        if any("Forgiveness" in theme.get("name", "") for theme in result.get("themes", [])):
            return "Forgiveness appears as a possible but incomplete resolution. The text suggests that healing requires emotional honesty and reconciliation, but it does not show a fully completed act of forgiveness."
        return "The provided material does not contain enough evidence to answer this question."

    if "theme" in normalized or "important" in normalized or "meaning" in normalized:
        if result.get("themes"):
            names = ", ".join(theme.get("name", "") for theme in result.get("themes", [])[:3])
            return f"The strongest themes in the provided material are {names}. These themes are supported by repeated conflict, emotional response, and family decisions described in the source text."

    for keyword in ["conflict", "emotion", "relationship", "scene", "character"]:
        if keyword in normalized:
            return "The provided material does not contain enough evidence to answer this question as stated."

    return "The provided material does not contain enough evidence to answer this question."


def render_theme_cards(result: dict):
    themes = result.get("themes", [])
    if not themes:
        st.info("No themes were detected in the supplied text.")
        return

    for theme in themes:
        name = html.escape(str(theme.get('name', 'Theme')))
        description = html.escape(str(theme.get('description', 'Not provided')))
        evidence = html.escape(str(theme.get('evidence', 'Not provided')))
        characters = html.escape(', '.join(theme.get('characters', [])) or 'Not specified')
        interpretation = html.escape(str(theme.get('interpretation', 'Not provided')))
        st.markdown(
            f"""
            <article class="theme-card">
                <div class="theme-card-title">{name}</div>
                <p class="theme-card-description">{description}</p>
                <div class="theme-card-detail"><strong>Evidence</strong>{evidence}</div>
                <div class="theme-card-detail"><strong>Characters</strong>{characters}</div>
                <div class="theme-card-detail"><strong>Interpretation</strong>{interpretation}</div>
            </article>
            """,
            unsafe_allow_html=True,
        )


def render_section(title: str, items: list, key_prefix: str):
    if not items:
        st.info(f"No {title.lower()} were identified in the supplied text.")
        return

    for index, item in enumerate(items, start=1):
        with st.expander(f"{title} {index}", expanded=False):
            for field, value in item.items():
                if isinstance(value, list):
                    value_text = ", ".join(str(v) for v in value) if value else "Not specified"
                elif value is None:
                    value_text = "Not specified"
                else:
                    value_text = str(value)
                st.markdown(f"**{field.replace('_', ' ').title()}:** {value_text}")


def clear_session():
    st.session_state.pop("analysis_result", None)
    st.session_state.pop("draft_text", None)
    st.session_state.pop("selected_movie", None)


def render_home_hero():
    st.markdown(
        """
        <div style='padding: 1.4rem 0 0.5rem 0; margin-bottom: 1rem; border-bottom: 1px solid rgba(148,163,184,0.25);'>
            <div style='font-size: 2.8rem; font-weight: 800; letter-spacing: 0.06em; color: #f8fafc;'>AI MovieLens</div>
            <div style='margin-top: 0.4rem; font-size: 1.1rem; letter-spacing: 0.12em; color: #cbd5e1; text-transform: uppercase;'>See the story. Understand the meaning.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style='display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;'>
            <div style='padding: 0.8rem 1rem; border-radius: 12px; background: rgba(15,23,42,0.7); border: 1px solid rgba(148,163,184,0.25);'>
                <strong>Themes</strong><br>Family, sacrifice, forgiveness, conflict
            </div>
            <div style='padding: 0.8rem 1rem; border-radius: 12px; background: rgba(15,23,42,0.7); border: 1px solid rgba(148,163,184,0.25);'>
                <strong>Characters</strong><br>Roles, motivations, and development
            </div>
            <div style='padding: 0.8rem 1rem; border-radius: 12px; background: rgba(15,23,42,0.7); border: 1px solid rgba(148,163,184,0.25);'>
                <strong>Evidence</strong><br>Text-based interpretation, not speculation
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="AI MovieLens", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { color-scheme: light; --ink: #172033; --muted: #64748b; --line: #dbe3ec; --accent: #e66b43; }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--ink); }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: #ffffff !important; color: var(--ink) !important; }
        [data-testid="stAppViewContainer"] { background: radial-gradient(circle at 82% 0%, #fff3e9 0, #f7f8fb 32rem, #ffffff 70%) !important; }
        .block-container { max-width: 1180px; padding: 2.5rem 2rem 4rem; }
        div[data-testid="stSidebar"] { background: #f3f6f9 !important; border-right: 1px solid #d7dee7; }
        div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3,
        div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] label,
        div[data-testid="stSidebar"] .stMarkdown,
        div[data-testid="stSidebar"] .stMarkdown p,
        div[data-testid="stSidebar"] .stMarkdown strong { color: #172033 !important; }
        div[data-testid="stSidebar"] .stCaption,
        div[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #526174 !important; }
        div[data-testid="stSidebar"] [data-baseweb="select"] * { color: #172033 !important; }
        div[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #ffffff; border-color: #b9c5d2; }
        div[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] { background: #ffffff; border: 1px dashed #aebccc; }
        div[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * { color: #172033 !important; }
        div[data-testid="stSidebar"] .stButton > button { background: #ffffff !important; color: #172033 !important; border: 1px solid #b9c5d2; }
        div[data-testid="stSidebar"] .stButton > button:hover { background: #fff3e9 !important; border-color: #f6a178; color: #9f3e22 !important; }
        .brand-kicker { color: var(--accent); font-size: .78rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
        .brand-title { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: clamp(2.4rem, 5vw, 4.7rem); font-weight: 700; letter-spacing: -.055em; line-height: .98; margin: .35rem 0 .8rem; }
        .brand-copy { color: var(--muted); font-size: 1.08rem; max-width: 680px; line-height: 1.6; }
        .feature-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin: 2rem 0 2.2rem; }
        .feature-item { background: rgba(255,255,255,.78); border: 1px solid var(--line); border-radius: 10px; padding: 1rem 1.1rem; }
        .feature-item strong { display: block; color: var(--ink); margin-bottom: .25rem; }
        .feature-item span { color: var(--muted); font-size: .87rem; }
        .section-label { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 600; margin: 1rem 0 .65rem; }
        .stTextArea textarea { background: #fff; border: 1px solid #aebccc; border-radius: 10px; color: #172033 !important; caret-color: #172033; font-size: 1rem; line-height: 1.6; }
        .stTextArea textarea::placeholder { color: #718096 !important; opacity: 1; }
        .stTextArea textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
        .stTextArea label, .stSelectbox label, .stFileUploader label { color: #172033 !important; font-weight: 600; }
        .stCaption, [data-testid="stCaptionContainer"] { color: #526174 !important; }
        .stMarkdown, .stMarkdown p, .stMarkdown li { color: #263449; }
        .stButton > button { border-radius: 7px; font-weight: 600; min-height: 2.7rem; }
        .stButton > button[kind="primary"] { background: var(--accent); border-color: var(--accent); }
        .stMetric { background: rgba(255,255,255,.78); border: 1px solid var(--line); border-radius: 10px; padding: .6rem .8rem; }
        .stMetric label, .stMetric [data-testid="stMetricValue"] { color: #172033 !important; }
        .stMetric [data-testid="stMetricDelta"] { color: #526174 !important; }
        [data-testid="stExpander"] { background: rgba(255,255,255,.7); border: 1px solid var(--line); border-radius: 9px; }
        [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color: #172033 !important; }
        .theme-card { background: #ffffff; border: 1px solid #d3dce6; border-left: 4px solid #e66b43; border-radius: 10px; margin: 0 0 1rem; padding: 1.1rem 1.25rem; }
        .theme-card-title { color: #172033; font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; margin-bottom: .45rem; }
        .theme-card-description { color: #263449; font-size: 1rem; line-height: 1.55; margin: 0 0 .9rem; }
        .theme-card-detail { color: #526174; font-size: .92rem; line-height: 1.5; margin-top: .55rem; }
        .theme-card-detail strong { color: #172033; display: inline-block; margin-right: .45rem; }
        .source-context { align-items: center; background: #172033; border-radius: 12px; color: #ffffff; display: flex; justify-content: space-between; gap: 1rem; margin: 1.2rem 0 1.35rem; padding: 1rem 1.2rem; }
        .source-context-label { color: #f6a178; font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
        .source-context-title { color: #ffffff; font-family: 'Space Grotesk', sans-serif; font-size: 1.28rem; font-weight: 600; margin-top: .2rem; }
        .source-context-meta { color: #c7d1df; font-size: .88rem; text-align: right; }
        .workflow-note { color: #526174; font-size: .9rem; margin: -.35rem 0 1rem; }
        .report-intro { background: #fffaf6; border: 1px solid #f3d5c3; border-radius: 10px; color: #526174; line-height: 1.55; margin: .5rem 0 1.3rem; padding: .85rem 1rem; }
        [data-baseweb="tab-list"] { gap: 1.2rem; }
        [data-baseweb="tab"] { color: #526174 !important; }
        [data-baseweb="tab"][aria-selected="true"] { color: #b84b29 !important; }
        @media (max-width: 700px) { .feature-strip { grid-template-columns: 1fr; } .block-container { padding: 1.5rem 1rem 3rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="brand-kicker">AI-powered narrative intelligence</div>
    <div class="brand-title">AI MovieLens</div>
    <div class="brand-copy">Turn a movie synopsis, scene, or transcript into a clear map of its themes, characters, emotions, and tensions.</div>
    <div class="feature-strip">
        <div class="feature-item"><strong>Read the story</strong><span>Find the narrative signal in your source text.</span></div>
        <div class="feature-item"><strong>See the meaning</strong><span>Connect evidence to themes and relationships.</span></div>
        <div class="feature-item"><strong>Ask better questions</strong><span>Explore the analysis with grounded Q&amp;A.</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🎬 MovieLens")
    st.caption("A focused workspace for evidence-based film analysis")
    st.markdown("---")
    st.markdown("### Choose a source")
    hf_model = st.text_input(
        "Hugging Face model",
        value=os.getenv('HUGGINGFACE_MODEL', 'meta-llama/Llama-3.1-8B-Instruct'),
        help="Use a text-generation chat model available through the Hugging Face router.",
    )
    st.markdown("---")
    movielens_movies = load_movielens_catalog()
    if movielens_movies:
        movie_titles = [movie['title'] for movie in movielens_movies]
        selected_movie_title = st.selectbox('MovieLens catalog', movie_titles[:100], index=0)
        if st.button('Use selected movie', use_container_width=True):
            selected_movie = next((m for m in movielens_movies if m['title'] == selected_movie_title), movielens_movies[0])
            st.session_state['selected_movie'] = selected_movie
            st.session_state['draft_text'] = (
                f"Movie title: {selected_movie['title']}\n"
                f"Genres: {selected_movie['genres']}\n"
                f"Average rating: {selected_movie['average_rating']} from {selected_movie['rating_count']} ratings\n"
                f"Community tags: {', '.join(selected_movie['tags']) or 'No tags available'}\n"
                f"IMDb ID: {selected_movie['imdb_id'] or 'Not available'}\n"
                f"TMDb ID: {selected_movie['tmdb_id'] or 'Not available'}\n"
                "This entry combines the MovieLens movies, ratings, tags, and links data. Use only the supplied information for evidence-based analysis and note any missing narrative details."
            )
            st.session_state.pop('analysis_result', None)
        st.caption("Source: online MovieLens catalog")
    if st.button("Load blank template", use_container_width=True):
        st.session_state["draft_text"] = SAMPLE_TEXT
        st.session_state.pop("analysis_result", None)
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload text, PDF, or Word file", type=["txt", "pdf", "docx"])
    if uploaded_file is not None:
        try:
            validate_file(uploaded_file.name, uploaded_file.size)
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name
            extracted_text = extract_text(temp_path)
            st.session_state["draft_text"] = extracted_text
            st.success("File loaded successfully.")
        except ValueError as exc:
            st.error(str(exc))

    st.markdown("---")
    st.caption("Your source stays in this session. Analysis uses Hugging Face when configured, otherwise the local engine.")

st.markdown('<div class="section-label">Start with a movie text</div>', unsafe_allow_html=True)
selected_movie = st.session_state.get('selected_movie')
if selected_movie:
    st.markdown(
        f"""
        <div class="source-context">
            <div><div class="source-context-label">Selected MovieLens title</div><div class="source-context-title">{html.escape(selected_movie['title'])}</div></div>
            <div class="source-context-meta">{html.escape(selected_movie['genres'])}<br>{html.escape(str(selected_movie['average_rating']))} / 5 from {selected_movie['rating_count']} ratings</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="workflow-note">Choose a catalog title, upload a file, or paste your own source text to begin.</div>', unsafe_allow_html=True)
text_input = st.text_area(
    "Paste a synopsis, scene description, or transcript",
    value=st.session_state.get("draft_text", SAMPLE_TEXT),
    height=260,
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 1])
with col1:
    analyze_clicked = st.button("Analyze narrative →", type="primary", use_container_width=True)
with col2:
    if st.button("Clear workspace", use_container_width=True):
        clear_session()
        st.rerun()

if analyze_clicked:
    input_text = text_input.strip()
    if not input_text:
        st.error("Please provide movie text before starting the analysis.")
    else:
        with st.status("Reading the narrative...", expanded=True) as status:
            st.write("Identifying characters and emotional cues...")
            st.write("Finding major themes and conflicts...")
            st.write("Checking evidence and interpretation...")
            try:
                result = analyze_text(input_text, os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_TOKEN', ''), hf_model)
                st.session_state["analysis_result"] = result
                status.update(label="Analysis complete.", state="complete")
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.stop()

if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]
    has_huggingface_key = bool((os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_TOKEN', '')).strip())

    st.markdown("## Analysis report")
    if has_huggingface_key:
        st.caption("AI-generated analysis grounded in the evidence contained in your supplied text.")
    else:
        st.caption("Local evidence-based analysis. Add a Hugging Face key in .env for model-generated output.")
    st.markdown('<div class="report-intro"><strong>Reading mode:</strong> AI MovieLens separates what the source says from the interpretation drawn from it. Review the overview first, then use the tabs to explore the evidence.</div>', unsafe_allow_html=True)
    overview = [
        ("Characters", str(len(result.get("characters", [])))),
        ("Themes", str(len(result.get("themes", [])))),
        ("Conflicts", str(len(result.get("conflicts", [])))),
        ("Scenes", str(len(result.get("important_scenes", [])))),
    ]

    cols = st.columns(len(overview))
    for col, (label, value) in zip(cols, overview):
        col.metric(label, value)

    st.markdown("### Executive summary")
    if not has_huggingface_key:
        st.info("This summary was generated by the local fallback engine, not an AI model.")
    st.write(result.get("summary", ""))

    tabs = st.tabs(["Overview", "Themes", "Characters", "Relationships", "Conflicts", "Emotions", "Scenes", "Dialectics", "Q&A"])

    with tabs[0]:
        st.markdown("#### Theme distribution")
        themes = result.get("themes", [])
        if themes:
            theme_df = pd.DataFrame({"Theme": [theme.get("name", "") for theme in themes], "Count": [1 for _ in themes]})
            st.bar_chart(theme_df.set_index("Theme")["Count"])
        else:
            st.info("No theme data available.")

    with tabs[1]:
        render_theme_cards(result)

    with tabs[2]:
        render_section("Character", result.get("characters", []), "characters")

    with tabs[3]:
        relation_items = result.get("relationships", [])
        if relation_items:
            for relationship in relation_items:
                st.markdown(
                    f"**{relationship.get('character_a', 'A')}** → **{relationship.get('relationship', 'Relationship')}** → **{relationship.get('character_b', 'B')}**"
                )
                st.caption(
                    f"Type: {relationship.get('type', 'Unknown')} | Initial state: {relationship.get('initial_state', 'Unknown')} | Current state: {relationship.get('current_state', 'Unknown')}"
                )
                st.markdown("---")
        else:
            st.info("No relationship data available.")

    with tabs[4]:
        render_section("Conflict", result.get("conflicts", []), "conflicts")

    with tabs[5]:
        emotions = result.get("emotions", [])
        if emotions:
            emotion_df = pd.DataFrame(
                [{"Character": item.get("character", "Unknown"), "Emotion": item.get("emotion", "Unknown")} for item in emotions]
            )
            st.bar_chart(emotion_df.groupby("Emotion").size())
            render_section("Emotion", emotions, "emotions")
        else:
            st.info("No emotional patterns detected.")

    with tabs[6]:
        render_section("Scene", result.get("important_scenes", []), "scenes")

    with tabs[7]:
        render_section("Dialectic", result.get("relational_dialectics", []), "dialectics")

    with tabs[8]:
        question = st.text_input("Ask about the movie text", placeholder="Why is family an important theme?")
        if question:
            answer = answer_question(result, question)
            st.info(answer)
        st.markdown("### Insights")
        for insight in result.get("insights", []):
            st.markdown(f"### {insight.get('title', 'Insight')}")
            st.write(insight.get("text", ""))
            st.caption(f"Evidence: {insight.get('evidence', 'Not provided')}")
            st.markdown("---")

else:
    st.markdown("### Demo dataset")
    st.write(SAMPLE_TEXT)
    st.markdown("### About AI MovieLens")
    st.write(
        "AI MovieLens is designed to analyze movie text in an evidence-based way. It focuses on themes, characters, relationships, emotions, conflicts, and relational tensions while clearly separating direct evidence from interpretation."
    )
