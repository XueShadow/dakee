import os
from typing import Any

from huggingface_hub import InferenceClient

DEFAULT_MODEL = 'meta-llama/Llama-3.1-8B-Instruct'
MAX_INPUT_LENGTH = 15000

SYSTEM_PROMPT = """You are a patient computer science instructor and algorithm analyst.
Explain only the algorithm or code supplied by the user. Do not execute code or claim to have benchmarked it.
If the input is ambiguous or incomplete, say what is unclear instead of inventing behavior.
Use clear Markdown with these sections:
## Purpose
## Core idea
## Step-by-step walkthrough
## Complexity
## Correctness and edge cases
Discuss time complexity (best, average, and worst case when meaningful) and auxiliary space. State assumptions that affect the analysis. Use a small, concrete example when the input allows one. Distinguish algorithm properties from details that depend on a particular implementation."""


def explain_algorithm(algorithm_text: str, api_key: str, model: str = DEFAULT_MODEL) -> str:
    source = (algorithm_text or '').strip()
    if not source:
        raise ValueError('Enter an algorithm name, pseudocode, or code sample.')
    if len(source) > MAX_INPUT_LENGTH:
        raise ValueError(f'Input must be {MAX_INPUT_LENGTH:,} characters or fewer.')

    token = (api_key or '').strip()
    if not token:
        raise ValueError('Set HUGGINGFACE_API_KEY in the project .env file to use the AI explainer.')

    selected_model = (model or DEFAULT_MODEL).strip()
    client = InferenceClient(
        provider='auto',
        model=selected_model,
        api_key=token,
        timeout=90,
    )
    try:
        response = client.chat_completion(
            model=selected_model,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': f'Explain this algorithm or code:\n\n{source}'},
            ],
            temperature=0.15,
            max_tokens=2200,
        )
    except Exception as exc:
        raise ValueError(
            f'Hugging Face inference failed: {exc}. Check your token, model, and available Inference Providers.'
        ) from exc

    choices: Any = getattr(response, 'choices', None)
    if not choices or not getattr(choices[0], 'message', None):
        raise ValueError('Hugging Face returned an empty explanation.')
    explanation = choices[0].message.content
    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError('Hugging Face returned an empty explanation.')
    return explanation.strip()
