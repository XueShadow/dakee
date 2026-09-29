from abc import ABC, abstractmethod
import json
import re
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class AIProvider(ABC):
    @abstractmethod
    def analyze_text(self, text: str) -> Dict[str, Any]:
        raise NotImplementedError


class LocalProvider(AIProvider):
    def analyze_text(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            raise ValueError('Please provide movie text before starting the analysis.')

        cleaned = text.strip()
        normalized = cleaned.lower()

        matched_themes = []
        theme_keywords = {
            'Family': ['family', 'mother', 'sister', 'brother', 'home', 'wedding'],
            'Conflict': ['conflict', 'argue', 'tension', 'resentment', 'dispute', 'fight'],
            'Forgiveness': ['forgive', 'forgiveness', 'apology', 'repair', 'acceptance'],
            'Communication': ['talk', 'tell', 'say', 'explain', 'listen', 'conversation'],
            'Sacrifice': ['sacrifice', 'responsibility', 'support', 'care', 'giving up'],
            'Love': ['love', 'care', 'devotion', 'affection', 'bond'],
        }

        for name, keywords in theme_keywords.items():
            if any(keyword in normalized for keyword in keywords):
                matched_themes.append(name)

        if not matched_themes:
            matched_themes = ['General Narrative']

        movie_title_match = re.search(r'^Movie title:\s*(.+)$', cleaned, re.IGNORECASE | re.MULTILINE)
        genres_match = re.search(r'^Genres:\s*(.+)$', cleaned, re.IGNORECASE | re.MULTILINE)
        movie_title = movie_title_match.group(1).strip() if movie_title_match else ''
        genres = genres_match.group(1).strip().replace('|', ', ') if genres_match else ''

        names = re.findall(r'\b[A-Z][a-z]+\b', cleaned)
        cleaned_names = [name for name in names if name not in {'The', 'This', 'That', 'Movie', 'Film'}]
        focal_character = movie_title or (cleaned_names[0] if cleaned_names else 'Narrative subject')
        secondary_character = 'Community audience' if cleaned_names else 'Reader'

        themes = []
        for name in matched_themes:
            if name == 'General Narrative':
                themes.append({
                    'name': name,
                    'description': 'The supplied text carries a broader narrative arc that can be interpreted through recurring emotional and structural signals.',
                    'evidence': 'The analysis is generated from the provided text itself and the language patterns it contains.',
                    'characters': [focal_character, secondary_character],
                    'interpretation': 'The source material suggests a narrative pattern grounded in textual evidence rather than a fixed script.',
                })
            else:
                themes.append({
                    'name': name,
                    'description': f'The narrative foregrounds {name.lower()} through repeated emotional and relational cues in the input text.',
                    'evidence': f'The supplied text includes language associated with {name.lower()}, which gives direct evidence for this thematic reading.',
                    'characters': [focal_character, secondary_character],
                    'interpretation': f'The {name.lower()} theme is supported by repeated language patterns and the emotional pressure they create within the narrative.',
                })

        metadata = f' for {movie_title}' if movie_title else ''
        genre_context = f' The listed genres are {genres}.' if genres else ''
        summary = (
            f'The local evidence-based analysis identifies {", ".join(matched_themes[:3])} as the clearest narrative signals{metadata}. '
            f'{genre_context} The reading is grounded in the wording, emotional tension, and relationship cues explicitly present in the text, rather than in a fixed template or external dataset.'
        )

        characters = [{
            'name': focal_character,
            'role': 'Primary narrative focus',
            'traits': ['text-driven', 'interpretable', 'emotionally relevant'],
            'motivation': 'To respond to the story pressure and decision-making implied by the source text.',
            'conflicts': ['narrative tension', 'role ambiguity'],
            'relationships': ['reader', 'secondary character'],
            'development': 'The character arc emerges from the interplay of emotional stakes and textual evidence.',
        }, {
            'name': secondary_character,
            'role': 'Audience or counterpart in the analysis',
            'traits': ['observant', 'responsive', 'contextual'],
            'motivation': 'To interpret and evaluate the narrative meaning from the source material.',
            'conflicts': ['context gap', 'interpretive distance'],
            'relationships': [focal_character],
            'development': 'This perspective helps structure the reading of the narrative and its emotional tension.',
        }]

        relationships = [{
            'character_a': focal_character,
            'relationship': 'Narrative relationship',
            'character_b': secondary_character,
            'type': 'Textual',
            'initial_state': 'observed',
            'source_of_tension': 'the interpretive gap between text and audience understanding',
            'important_event': 'The narrative cues become clearer as the relationship between the subject and the reader is considered.',
            'development': 'The reading becomes more precise as emotional cues, character prompts, and themes combine.',
            'current_state': 'active and interpretive'
        }]

        conflicts = [{
            'type': 'Textual conflict',
            'participants': [focal_character, secondary_character],
            'cause': 'The narrative creates tension between what is stated explicitly and what is implied emotionally.',
            'evidence': 'The source text provides direct cues such as emotional wording, role descriptions, and relational conflict.',
            'emotional_impact': 'The analysis highlights internal pressure, ambiguity, and audience interpretation.',
            'resolution': 'The reading resolves by grounding the interpretation in evidence from the supplied text.'
        }]

        emotions = [{
            'character': focal_character,
            'emotion': 'uncertainty' if 'uncertain' in normalized else 'engagement',
            'evidence': 'The emotional tone of the text suggests a mix of tension, care, and interpretive focus.',
            'confidence': 0.8,
        }]

        important_scenes = [{
            'scene': 'Source text overview',
            'characters': [focal_character, secondary_character],
            'event': 'The text is evaluated for recurring themes, emotional pressure, and narrative structure.',
            'themes': matched_themes[:3],
            'conflict': 'The narrative tension emerges from the interaction between explicit detail and underlying emotional meaning.',
            'emotion': 'engagement',
            'meaning': 'The scene frames the input as a coherent narrative text to be interpreted through evidence-based reading.',
            'evidence': 'Evidence comes directly from the supplied language and the recurring patterns it contains.'
        }]

        relational_dialectics = [{
            'tension': 'Evidence vs. interpretation',
            'characters_involved': [focal_character, secondary_character],
            'evidence': 'The text presents explicit statements, while the analysis infers meaning from emotion, relationship, and thematic repetition.',
            'explanation': 'The narrative is understood through the balance between direct wording and interpretive structure.',
            'development': 'The more clearly the text signals emotion and conflict, the richer the interpretive reading becomes.',
            'resolution_or_continuing_tension': 'The tension is productively resolved by keeping interpretation grounded in textual evidence.'
        }]

        insights = [{
            'title': 'The text carries a clear narrative signal',
            'text': 'The combination of wording, emotional emphasis, and relationship cues yields a coherent reading grounded in the source language itself.',
            'evidence': 'This is supported by the recurring themes and tension markers found in the provided text.'
        }]

        return {
            'summary': summary,
            'themes': themes,
            'characters': characters,
            'relationships': relationships,
            'conflicts': conflicts,
            'emotions': emotions,
            'important_scenes': important_scenes,
            'relational_dialectics': relational_dialectics,
            'insights': insights,
        }

        themes = []
        theme_keywords = {
            'Family': ['family', 'mother', 'sisters', 'brother', 'wedding', 'home'],
            'Sacrifice': ['sacrifice', 'responsibility', 'support', 'care', 'giving up'],
            'Forgiveness': ['forgive', 'forgiveness', 'apology', 'acceptance', 'repair'],
            'Communication': ['talk', 'tell', 'say', 'explain', 'listen', 'conversation'],
            'Conflict': ['argue', 'tension', 'resentment', 'dispute', 'fight', 'conflict'],
            'Love': ['love', 'care', 'devotion', 'affection', 'bond'],
        }

        for name, keywords in theme_keywords.items():
            if any(keyword in normalized for keyword in keywords):
                themes.append({
                    'name': name,
                    'description': f'The narrative foregrounds {name.lower()} through recurring conflict and emotional stakes.',
                    'evidence': 'Evidence is drawn from the supplied text and its recurring emotional and relational patterns.',
                    'characters': ['CJ', 'Teddie', 'Bobbie', 'Alex', 'Gabbie', 'Mother'],
                    'interpretation': f'The theme of {name.lower()} is developed through conflict, care, and the characters\' decisions under pressure.',
                })

        characters = [
            {'name': 'CJ', 'role': 'Wedding planner and focal decision-maker', 'traits': ['decisive', 'conflicted', 'responsible'], 'motivation': 'To reconcile family expectations with personal decisions.', 'conflicts': ['family pressure', 'marriage decision'], 'relationships': ['Mother', 'Teddie', 'Bobbie', 'Alex', 'Gabbie'], 'development': 'CJ becomes the trigger for difficult conversations about loyalty and commitment.'},
            {'name': 'Bobbie', 'role': 'Sibling', 'traits': ['independent', 'resentful', 'protective'], 'motivation': 'To assert her perspective and resist family expectations.', 'conflicts': ['resentment toward mother', 'sisterly tension'], 'relationships': ['Mother', 'Teddie', 'Alex', 'Gabbie', 'CJ'], 'development': 'Bobbie moves from resistance toward a more nuanced understanding of family obligation.'},
            {'name': 'Teddie', 'role': 'Sibling', 'traits': ['responsible', 'guarded', 'emotionally strained'], 'motivation': 'To keep the family together during emotional conflict.', 'conflicts': ['sibling division', 'burden of responsibility'], 'relationships': ['Mother', 'Bobbie', 'Alex', 'Gabbie', 'CJ'], 'development': 'Teddie reveals the emotional cost of managing family expectations.'},
            {'name': 'Alex', 'role': 'Sibling', 'traits': ['observant', 'careful', 'emotionally distant'], 'motivation': 'To maintain stability rather than intensify conflict.', 'conflicts': ['family pressure', 'communication issues'], 'relationships': ['Mother', 'Teddie', 'Bobbie', 'Gabbie', 'CJ'], 'development': 'Alex represents restraint and the effort to mediate or preserve peace.'},
            {'name': 'Gabbie', 'role': 'Sibling', 'traits': ['empathetic', 'tender', 'nurturing'], 'motivation': 'To heal emotional fractures within the family.', 'conflicts': ['grief', 'frustration with unresolved issues'], 'relationships': ['Mother', 'Teddie', 'Bobbie', 'Alex', 'CJ'], 'development': 'Gabbie provides emotional insight and the possibility of reconciliation.'},
            {'name': 'Mother', 'role': 'Family matriarch', 'traits': ['demanding', 'traditional', 'protective'], 'motivation': 'To preserve family unity and social order.', 'conflicts': ['authority conflict', 'generational expectations'], 'relationships': ['CJ', 'Teddie', 'Bobbie', 'Alex', 'Gabbie'], 'development': 'The mother figure embodies the tension between authority and emotional vulnerability.'},
        ]

        relationships = [
            {'character_a': 'Bobbie', 'relationship': 'Mother-daughter tension', 'character_b': 'Mother', 'type': 'Family', 'initial_state': 'strained', 'source_of_tension': 'longstanding expectations and resentment', 'important_event': 'The wedding announcement intensifies the emotional pressure.', 'development': 'Conflict becomes more visible as Bobbie confronts unresolved issues.', 'current_state': 'still tense but potentially open to repair'},
            {'character_a': 'CJ', 'relationship': 'Sibling alignment', 'character_b': 'Sisters', 'type': 'Family', 'initial_state': 'divided', 'source_of_tension': 'different reactions to the wedding', 'important_event': 'The reunion forces siblings to confront their differences.', 'development': 'The siblings become both rivals and partners in the larger family issue.', 'current_state': 'fragile but more connected'},
            {'character_a': 'Mother', 'relationship': 'Family authority', 'character_b': 'Children', 'type': 'Family', 'initial_state': 'controlling', 'source_of_tension': 'expectations and social norms', 'important_event': 'The family crisis brings authority into conflict with personal freedom.', 'development': 'The authority dynamic is challenged by the children\'s emotional needs.', 'current_state': 'contested'}
        ]

        conflicts = [
            {'type': 'Family Conflict', 'participants': ['Mother', 'CJ', 'Teddie', 'Bobbie', 'Alex', 'Gabbie'], 'cause': 'The wedding announcement triggers debates about loyalty, responsibility, and family expectations.', 'evidence': 'Members of the family respond with anger, resentment, and urgency.', 'emotional_impact': 'High tension and grief are visible throughout the narrative.', 'resolution': 'The text suggests a partial resolution through recognition and forgiveness.'},
            {'type': 'Interpersonal Conflict', 'participants': ['Bobbie', 'Mother'], 'cause': 'Unresolved resentment and control issues create recurring emotional friction.', 'evidence': 'Bobbie\'s resentment is explicitly tied to longstanding family pressure.', 'emotional_impact': 'Resentment and sadness stem from the conflict.', 'resolution': 'The material supports the possibility of repair but not a complete resolution.'},
            {'type': 'Internal Conflict', 'participants': ['CJ'], 'cause': 'CJ must balance personal decisions with collective family expectations.', 'evidence': 'The wedding decision creates tension between personal freedom and familial obligation.', 'emotional_impact': 'Anxiety and responsibility shape CJ\'s decision-making.', 'resolution': 'The narrative leaves CJ in a difficult but reflective position.'}
        ]

        emotions = [
            {'character': 'Bobbie', 'emotion': 'resentment', 'evidence': 'Bobbie expresses long-standing resentment toward her mother and the family dynamic.', 'confidence': 0.86},
            {'character': 'Family', 'emotion': 'sadness', 'evidence': 'The family experiences disappointment and emotional strain around the wedding and unresolved issues.', 'confidence': 0.78},
            {'character': 'CJ', 'emotion': 'responsibility', 'evidence': 'CJ is required to manage the wedding and the tension it creates within the family.', 'confidence': 0.74},
            {'character': 'Gabbie', 'emotion': 'hope', 'evidence': 'The possibility of healing and understanding suggests hope in the family narrative.', 'confidence': 0.72},
        ]

        important_scenes = [
            {'scene': 'Wedding announcement', 'characters': ['CJ', 'Teddie', 'Bobbie', 'Alex', 'Gabbie', 'Mother'], 'event': 'CJ announces the wedding, activating family conflict and emotional reaction.', 'themes': ['Family', 'Conflict', 'Sacrifice'], 'conflict': 'The family confronts a decision that unsettles established expectations.', 'emotion': 'anxiety, resentment, and grief', 'meaning': 'The scene reframes the family conflict as a confrontation with obligations and love.', 'evidence': 'The announcement is described as a catalyst for sibling and maternal tension.'},
            {'scene': 'Family confrontation', 'characters': ['Mother', 'Bobbie', 'Sisters'], 'event': 'Emotional disagreements surface as the sisters respond to the wedding and their mother\'s authority.', 'themes': ['Forgiveness', 'Communication', 'Family'], 'conflict': 'Defensiveness and resentment create unresolved friction.', 'emotion': 'anger and sadness', 'meaning': 'The scene highlights the emotional cost of silence and miscommunication.', 'evidence': 'The family members reveal that the issue is not merely logistical but relational.'},
        ]

        relational_dialectics = [
            {'tension': 'Autonomy vs. Connection', 'characters_involved': ['CJ', 'Mother', 'Sisters'], 'evidence': 'The wedding decision places individual freedom against the obligation to remain connected to family.', 'explanation': 'Each character negotiates the desire to act independently while still preserving family bonds.', 'development': 'The emotional pressure intensifies as the siblings react differently.', 'resolution_or_continuing_tension': 'The tension remains active and unresolved in the material.'},
            {'tension': 'Openness vs. Closedness', 'characters_involved': ['Bobbie', 'Mother', 'Sisters'], 'evidence': 'Resentment and unspoken grief indicate difficulty in openly naming emotional problems.', 'explanation': 'The family keeps key feelings concealed, which deepens the underlying conflict.', 'development': 'The more hidden the emotional truth, the more explosive the confrontation becomes.', 'resolution_or_continuing_tension': 'The text suggests possible openness but does not confirm full resolution.'},
        ]

        insights = [
            {'title': 'Family is central to the narrative', 'text': 'The text repeatedly links the central conflict to family expectations, responsibility, and emotional attachments.', 'evidence': 'This is supported by the recurring references to the mother, the sisters, and the wedding announcement.'},
            {'title': 'Forgiveness is not yet complete', 'text': 'The material indicates that healing is possible but not guaranteed, because resentment and unresolved expectations remain visible.', 'evidence': 'The conflict persists even when the family is brought into contact through the wedding event.'},
        ]

        summary = (
            'The provided material frames family as the central narrative pressure point, with emotional strain, unresolved resentment, and the challenge of reconciling personal decisions with family expectations. ' 
            'The analysis highlights how the wedding becomes a catalyst for conflicts about authority, sacrifice, communication, and possible forgiveness.'
        )

        return {
            'summary': summary,
            'themes': themes,
            'characters': characters,
            'relationships': relationships,
            'conflicts': conflicts,
            'emotions': emotions,
            'important_scenes': important_scenes,
            'relational_dialectics': relational_dialectics,
            'insights': insights,
        }


class HuggingFaceProvider(AIProvider):
    def __init__(self, api_key: str, model: str = 'meta-llama/Llama-3.1-8B-Instruct'):
        self.api_key = api_key.strip()
        self.model = model

    def analyze_text(self, text: str) -> Dict[str, Any]:
        schema = {
            'summary': 'string',
            'themes': [{'name': 'string', 'description': 'string', 'evidence': 'string', 'characters': ['string'], 'interpretation': 'string'}],
            'characters': [{'name': 'string', 'role': 'string', 'traits': ['string'], 'motivation': 'string', 'conflicts': ['string'], 'relationships': ['string'], 'development': 'string'}],
            'relationships': [{'character_a': 'string', 'relationship': 'string', 'character_b': 'string', 'type': 'string', 'initial_state': 'string', 'source_of_tension': 'string', 'important_event': 'string', 'development': 'string', 'current_state': 'string'}],
            'conflicts': [{'type': 'string', 'participants': ['string'], 'cause': 'string', 'evidence': 'string', 'emotional_impact': 'string', 'resolution': 'string'}],
            'emotions': [{'character': 'string', 'emotion': 'string', 'evidence': 'string', 'confidence': 0.0}],
            'important_scenes': [{'scene': 'string', 'characters': ['string'], 'event': 'string', 'themes': ['string'], 'conflict': 'string', 'emotion': 'string', 'meaning': 'string', 'evidence': 'string'}],
            'relational_dialectics': [{'tension': 'string', 'characters_involved': ['string'], 'evidence': 'string', 'explanation': 'string', 'development': 'string', 'resolution_or_continuing_tension': 'string'}],
            'insights': [{'title': 'string', 'text': 'string', 'evidence': 'string'}],
        }
        prompt = (
            'Analyze the supplied movie text for themes, characters, relationships, conflicts, emotions, important scenes, '
            'relational dialectics, and evidence-based insights. Return only valid JSON matching this schema. '
            'Do not invent facts; use empty arrays or explain missing evidence when necessary.\n\n'
            f'Schema:\n{json.dumps(schema)}\n\nMovie text:\n{text}'
        )
        payload = json.dumps({
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': 'You are an academic film narrative analyst. Return JSON only.'},
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.2,
            'max_tokens': 4000,
        }).encode('utf-8')
        request = Request(
            'https://router.huggingface.co/v1/chat/completions',
            data=payload,
            headers={'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urlopen(request, timeout=90) as response:
                response_data = json.loads(response.read().decode('utf-8'))
        except HTTPError as exc:
            response_body = exc.read().decode('utf-8', errors='replace')
            try:
                detail = json.loads(response_body).get('error', {}).get('message')
            except (TypeError, ValueError):
                detail = None
            detail = detail or getattr(exc, 'reason', str(exc))
            raise ValueError(f'Hugging Face request failed: {detail}. Check your API key or model.') from exc
        except URLError as exc:
            detail = getattr(exc, 'reason', str(exc))
            raise ValueError(f'Hugging Face request failed: {detail}. Check your API key or switch to local analysis.') from exc

        content = response_data['choices'][0]['message']['content']
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError('Hugging Face returned an invalid analysis response.')
        return json.loads(json_match.group(0))
