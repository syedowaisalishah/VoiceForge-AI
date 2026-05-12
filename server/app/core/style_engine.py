import json
import os
from typing import List, Dict
import random

class StyleEngine:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.personas = self._load_data()

    def _load_data(self) -> Dict:
        personas = {}
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".json") and filename != "personas.json":
                    persona_id = filename.replace(".json", "")
                    with open(os.path.join(os.path.join(self.data_dir, filename)), 'r') as f:
                        personas[persona_id] = json.load(f)
        return personas

    def construct_prompt(self, persona_id: str, platform: str, brief: str) -> str:
        p = self.personas.get(persona_id)
        if not p:
            raise ValueError(f"Persona {persona_id} not found")

        # Extract detailed persona components
        persona_info = p.get("persona", {})
        tone = p.get("tone", {})
        vocab = p.get("vocabulary", {})
        structure = p.get("structure", {})
        emojis = p.get("emoji_usage", {})
        instructions = p.get("prompt_instructions", {})
        examples = p.get("example_posts", [])

        # Format Examples
        sample_size = min(len(examples), 5)
        samples = random.sample(examples, sample_size)
        formatted_examples = "\n\n".join([f"TYPE: {ex.get('type')}\nPOST: {ex.get('post')}" for ex in samples])

        # Build the Ultra-Detailed Prompt
        system_msg = instructions.get("system_prompt", "You are an expert ghostwriter.")
        
        prompt = f"""
{system_msg}

WRITER IDENTITY:
- Name: {persona_info.get('name')}
- Niche: {persona_info.get('niche')}
- Account Type: {persona_info.get('account_type')}

TONE RULES:
- Overall: {tone.get('overall')}
- Do use: {', '.join(tone.get('descriptors', []))}
- NEVER use: {', '.join(tone.get('never', []))}

VOCABULARY & STYLE:
- Signature Phrases: {', '.join(vocab.get('signature_phrases', []))}
- Number Style: {vocab.get('number_style')}
- Profanity: {vocab.get('profanity_level')}

STRUCTURE & FORMATTING:
- Line Breaks: {structure.get('line_break_style')}
- Opening Style: {random.choice(structure.get('opening_patterns', ['Bold hook']))}
- Closing Style: {random.choice(structure.get('closing_patterns', ['Grateful close']))}

EMOJI RULES:
- Rules: {', '.join(emojis.get('rules', []))}
- Common Emojis: {', '.join(emojis.get('common_emojis', []))}

REAL EXAMPLES OF {persona_info.get('name').upper()}:
{formatted_examples}

THE BRIEF (Context provided by user):
{brief}

FINAL CONSTRAINTS:
{chr(10).join([f"- {rule}" for rule in instructions.get('output_rules', [])])}

Write the {platform} post now:
"""
        return prompt.strip()
