import json
import os
from typing import Dict, Optional

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
                    with open(os.path.join(self.data_dir, filename), 'r') as f:
                        personas[persona_id] = json.load(f)
        return personas

    def get_post_types(self, persona_id: str) -> list:
        """Return available post types for a persona."""
        p = self.personas.get(persona_id, {})
        post_types = p.get("post_types", {})
        result = []
        for type_key, type_data in post_types.items():
            result.append({
                "id": type_key,
                "label": type_key.replace("_", " ").title(),
                "description": type_data.get("description", "")
            })
        return result

    def construct_prompt(
        self,
        persona_id: str,
        platform: str,
        brief: str,
        post_type: Optional[str] = None,
        mood: Optional[str] = None
    ) -> str:
        p = self.personas.get(persona_id)
        if not p:
            raise ValueError(f"Persona '{persona_id}' not found")

        # ── Extract all sections from the JSON ──────────────────────────────
        persona_info   = p.get("persona", {})
        tone           = p.get("tone", {})
        vocab          = p.get("vocabulary", {})
        structure      = p.get("structure", {})
        emoji_usage    = p.get("emoji_usage", {})
        post_types     = p.get("post_types", {})
        instructions   = p.get("prompt_instructions", {})
        examples       = p.get("example_posts", [])
        motifs         = p.get("recurring_motifs", {})
        diff_key       = "alex_vs_zack_critical_differences" if "alex" in persona_id else "zack_vs_alex_critical_differences"
        differences    = p.get(diff_key, p.get("alex_vs_zack_critical_differences", p.get("zack_vs_alex_critical_differences", {})))

        # ── System prompt ───────────────────────────────────────────────────
        system_msg = instructions.get("system_prompt", "You are an expert ghostwriter.")

        # ── Voice summary ───────────────────────────────────────────────────
        voice_summary = persona_info.get("voice_summary", "")

        # ── Tone section ────────────────────────────────────────────────────
        tone_overall     = tone.get("overall", "")
        tone_descriptors = tone.get("descriptors", [])
        tone_never       = tone.get("never", [])

        # ── Vocabulary ──────────────────────────────────────────────────────
        sig_phrases   = vocab.get("signature_phrases", [])
        common_words  = vocab.get("common_words", [])
        profanity_lvl = vocab.get("profanity_level", "")
        profanity_ex  = vocab.get("profanity_examples", [])
        number_style  = vocab.get("number_style", "")
        punct_style   = vocab.get("punctuation_style", "")

        # ── Structure (using the CORRECT key names from the JSON) ───────────
        opening_patterns = structure.get("opening_patterns", [])
        body_patterns    = structure.get("body_patterns", [])
        closing_patterns = structure.get("closing_patterns", [])
        line_break_rules = structure.get("line_break_rules", [])  # FIXED: was 'line_break_style'

        # ── Emoji rules (using the CORRECT nested structure from the JSON) ──
        emoji_freq       = emoji_usage.get("frequency", "")
        emoji_placement  = emoji_usage.get("placement", "")
        emoji_rules_dict = emoji_usage.get("emoji_rules", {})     # FIXED: was 'rules'
        emoji_never      = emoji_usage.get("never", [])
        # Format the emoji rules dict into readable lines
        emoji_rules_lines = [f"  • {k}: {v}" for k, v in emoji_rules_dict.items()]

        # ── Post type specific guidance ─────────────────────────────────────
        post_type_block = ""
        if post_type and post_type in post_types:
            pt = post_types[post_type]
            pt_description = pt.get("description", "")
            pt_format      = pt.get("format", pt.get("key_elements", []))
            pt_rules       = pt.get("rules", [])
            pt_example     = pt.get("example", "")

            format_lines = "\n".join([f"  {i+1}. {line}" for i, line in enumerate(pt_format)])
            rules_lines  = "\n".join([f"  - {r}" for r in pt_rules]) if pt_rules else ""
            example_block = f"\n  EXAMPLE:\n  {pt_example}" if pt_example else ""

            post_type_block = f"""
REQUESTED POST TYPE: {post_type.upper().replace('_', ' ')}
Description: {pt_description}
Required format/elements:
{format_lines}
{rules_lines}{example_block}
"""

        # ── Mood ────────────────────────────────────────────────────────────
        mood_block = f"\nMOOD FOR THIS POST: {mood.upper()}" if mood else ""

        # ── Recurring motifs ────────────────────────────────────────────────
        motifs_list = motifs.get("motifs", [])
        motifs_block = ""
        if motifs_list:
            motifs_lines = "\n".join([f"  - {m}" for m in motifs_list])
            motifs_block = f"""
RECURRING MOTIFS (weave in naturally if relevant — never force them):
{motifs_lines}
"""

        # ── Alex vs Zack critical differences ──────────────────────────────
        persona_name = persona_info.get("name", persona_id.capitalize())
        diff_this    = differences.get(persona_id, differences.get(persona_name.lower(), []))
        other_id     = "zack" if "alex" in persona_id else "alex"
        other_name   = "Zack" if "alex" in persona_id else "Alex"
        diff_other   = differences.get(other_id, differences.get(other_name.lower(), []))

        diff_block = ""
        if diff_this or diff_other:
            this_lines  = "\n".join([f"  ✓ {d}" for d in diff_this])
            other_lines = "\n".join([f"  ✗ {d}" for d in diff_other])
            diff_block = f"""
CRITICAL PERSONA SEPARATION (these are absolute rules):
{persona_name.upper()} DOES:
{this_lines}

{other_name.upper()} DOES (NEVER bleed these into {persona_name}'s posts):
{other_lines}
"""

        # ── Examples: select up to 10, prioritise matching post type ────────
        type_examples  = [ex for ex in examples if ex.get("type") == post_type] if post_type else []
        other_examples = [ex for ex in examples if ex.get("type") != post_type]

        # Take up to 3 type-matching, pad with other examples up to 10 total
        selected = type_examples[:3]
        remaining_slots = 10 - len(selected)
        selected += other_examples[:remaining_slots]

        formatted_examples = "\n\n---\n".join([
            f"[EXAMPLE — type: {ex.get('type')}]\n{ex.get('post', '')}"
            for ex in selected
        ])

        # ── Opening / closing patterns (all of them, not a random pick) ─────
        openings_block = "\n".join([f"  • {p}" for p in opening_patterns])
        closings_block = "\n".join([f"  • {p}" for p in closing_patterns])
        body_block     = "\n".join([f"  • {p}" for p in body_patterns])
        breaks_block   = "\n".join([f"  • {r}" for r in line_break_rules])

        # ── Hallucination firewall ──────────────────────────────────────────
        hallucination_firewall = """
════════════════════════════════════════════════════════════
HALLUCINATION FIREWALL — NON-NEGOTIABLE HARD RULES:
════════════════════════════════════════════════════════════
1. Use ONLY the facts explicitly listed in THE BRIEF below. Zero exceptions.
2. Do NOT invent dollar amounts, percentages, timeframes, or revenue figures not provided.
3. Do NOT invent job details, client names/reactions, or story outcomes not given.
4. Do NOT invent statistics, claims, quotes, or references to other people.
5. If the brief is vague or light on detail, write a SHORTER, TIGHTER post — never pad with invented content.
6. Do NOT add lessons, anecdotes, or business wisdom beyond what the brief implies.
7. If a number is not given, do not write a number. Period.
════════════════════════════════════════════════════════════
"""

        # ── Anti-AI-sounding block ──────────────────────────────────────────
        anti_ai_block = """
ANTI-AI QUALITY GATE — reject any draft that contains these:
  ✗ "In today's competitive landscape..."
  ✗ "It's important to remember..."
  ✗ "One thing I've learned is..."
  ✗ "As an entrepreneur..."
  ✗ "This journey has taught me..."
  ✗ "In conclusion..."
  ✗ "I'm excited to share..."
  ✗ "I wanted to take a moment..."
  ✗ Any word not in the vocabulary section above (esp: leverage, optimize, synergy, monetize)
  ✗ Generic motivational filler not drawn from the signature_phrases list above
  ✗ Any complete sentence that could appear in a generic AI social media post
"""

        # ── Output rules from JSON ──────────────────────────────────────────
        output_rules = instructions.get("output_rules", [])
        output_rules_block = "\n".join([f"  - {r}" for r in output_rules])

        # ── Assemble the full prompt ────────────────────────────────────────
        prompt = f"""{system_msg}

════════════════════════════════════════════════════════════
WRITER IDENTITY
════════════════════════════════════════════════════════════
Name: {persona_name}
Handle: {persona_info.get('handle', '')}
Platform: {persona_info.get('platform', platform)}
Niche: {persona_info.get('niche', '')}
Account type: {persona_info.get('account_type', '')}

CORE VOICE:
{voice_summary}

════════════════════════════════════════════════════════════
TONE RULES
════════════════════════════════════════════════════════════
Overall: {tone_overall}

DO use these qualities:
{chr(10).join([f'  • {d}' for d in tone_descriptors])}

NEVER:
{chr(10).join([f'  ✗ {n}' for n in tone_never])}

════════════════════════════════════════════════════════════
VOCABULARY & STYLE
════════════════════════════════════════════════════════════
Signature phrases (use naturally, not forced):
  {' | '.join(sig_phrases)}

Common words this writer uses:
  {', '.join(common_words)}

Number style: {number_style}
Punctuation style: {punct_style}
Profanity level: {profanity_lvl}
Profanity examples (for reference, not mandatory):
  {' | '.join(profanity_ex)}

════════════════════════════════════════════════════════════
STRUCTURE & FORMATTING
════════════════════════════════════════════════════════════
LINE BREAK RULES:
{breaks_block}

OPENING PATTERNS (pick the most appropriate for the brief):
{openings_block}

BODY PATTERNS (use the most appropriate for the post type):
{body_block}

CLOSING PATTERNS (pick the most appropriate for the mood):
{closings_block}

════════════════════════════════════════════════════════════
EMOJI RULES
════════════════════════════════════════════════════════════
Frequency: {emoji_freq}
Placement: {emoji_placement}

Allowed emojis and when to use them:
{chr(10).join(emoji_rules_lines)}

NEVER use emojis:
{chr(10).join([f'  ✗ {n}' for n in emoji_never])}
{diff_block}{motifs_block}{post_type_block}{mood_block}
════════════════════════════════════════════════════════════
REAL EXAMPLES OF {persona_name.upper()}'S ACTUAL POSTS
════════════════════════════════════════════════════════════
Study these carefully. Match the rhythm, vocabulary, and structure — not just the topic.

{formatted_examples}

{hallucination_firewall}
════════════════════════════════════════════════════════════
THE BRIEF — user-supplied context (your ONLY factual source)
════════════════════════════════════════════════════════════
{brief}

════════════════════════════════════════════════════════════
OUTPUT RULES
════════════════════════════════════════════════════════════
{output_rules_block}
{anti_ai_block}
Now write the {platform} post for {persona_name}. Output the post text only — no preamble, no explanation, no quotes around the post:"""

        return prompt.strip()
