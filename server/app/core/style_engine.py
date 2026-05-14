import json
import os
from typing import Dict, Optional

# ── Tone definitions ─────────────────────────────────────────────────────────
TONES = [
    {
        "id": "raw",
        "label": "Raw & Unfiltered",
        "emoji": "🔥",
        "description": "No polish. Like a voice note turned to text. Incomplete sentences OK.",
        "prompt_hint": "Write like you're venting out loud. Incomplete sentences are fine. Zero corporate polish. No transitions. Just the thought, dropped raw.",
    },
    {
        "id": "story",
        "label": "Story",
        "emoji": "📖",
        "description": "Narrative arc — setup, what happened, the turn.",
        "prompt_hint": "Structure as a mini story: set the scene, build tension or contrast, land with the turn or punchline. Every sentence moves forward.",
    },
    {
        "id": "controversial",
        "label": "Controversial Take",
        "emoji": "⚡",
        "description": "Bold claim people will quote or argue with.",
        "prompt_hint": "Lead with a bold, slightly uncomfortable claim. Don't hedge. Make it quotable and debate-worthy. No softening qualifiers.",
    },
    {
        "id": "humble_brag",
        "label": "Humble Brag",
        "emoji": "😏",
        "description": "Achievement, but grounded and self-aware.",
        "prompt_hint": "Share the win, but stay grounded. Acknowledge the hard part or the cost. Make it feel earned, not showboated.",
    },
    {
        "id": "rant",
        "label": "Rant",
        "emoji": "😤",
        "description": "Controlled frustration released with clarity.",
        "prompt_hint": "Frustration is the engine. Get specific about what's wrong. Short punchy sentences. Build intensity. Don't resolve it neatly.",
    },
    {
        "id": "lesson",
        "label": "Lesson Learned",
        "emoji": "💡",
        "description": "Retrospective — what happened and what it taught.",
        "prompt_hint": "Start with the mistake or situation. End with the specific insight. Keep it concrete — no generic wisdom.",
    },
    {
        "id": "hype",
        "label": "Hype",
        "emoji": "🚀",
        "description": "Big energy. Announcement or momentum-building.",
        "prompt_hint": "High energy from line one. Short punchy lines. Build momentum. Make it feel like something is happening right now.",
    },
    {
        "id": "question",
        "label": "Question / Open Loop",
        "emoji": "🤔",
        "description": "Opens a conversation. Ends with a hook or question.",
        "prompt_hint": "Set up a tension or observation, then end with a genuine question or open loop that makes people want to reply. Don't answer your own question.",
    },
]

# ── Audience definitions ──────────────────────────────────────────────────────
AUDIENCES = [
    {
        "id": "founders",
        "label": "Entrepreneurs / Founders",
        "emoji": "💼",
        "prompt_hint": "Reader is a fellow founder or operator. Speak peer-to-peer. No hand-holding. Use ops/business language naturally. They understand risk, margins, and hiring pain.",
    },
    {
        "id": "beginners",
        "label": "Beginners / New People",
        "emoji": "🌱",
        "prompt_hint": "Reader is just starting out. Avoid jargon. If you use a business term, make it clear from context. Be relatable and encouraging without being patronizing.",
    },
    {
        "id": "service_biz",
        "label": "Service Business Owners",
        "emoji": "🔧",
        "prompt_hint": "Reader runs a service business — cleaning, landscaping, trades, etc. Ops-heavy references land well. Mention scheduling, labor, job costs, and margins naturally.",
    },
    {
        "id": "personal_brand",
        "label": "Personal Brand Builders",
        "emoji": "📱",
        "prompt_hint": "Reader is building their own audience or online presence. Meta-commentary about content, posting, and growth is relatable to them.",
    },
    {
        "id": "general",
        "label": "General Public",
        "emoji": "🌍",
        "prompt_hint": "Anyone could be reading. Keep it universal and simple. No industry jargon. Make the stakes obvious without explaining business basics.",
    },
    {
        "id": "custom",
        "label": "Custom (specify below)",
        "emoji": "✏️",
        "prompt_hint": "",  # filled dynamically
    },
]

# ── X Format definitions ──────────────────────────────────────────────────────
X_FORMATS = [
    {
        "id": "two_liner",
        "label": "2-Liner",
        "emoji": "⚡",
        "description": "Punchy. Under 140 chars. No explanation.",
        "preview": "── ────────────────────────\n── ─────────────────",
        "prompt_hint": """FORMAT: 2-LINER (STRICT)
HARD RULES — any violation means the output is rejected:
  • Exactly 2 lines. Not 3. Not 4. Two.
  • Total character count MUST be under 200 characters including line break.
  • No hashtags. No emojis unless the persona always uses one.
  • No explanation, no context, no setup beyond line 1.
  • Line 1 = the hook or statement. Line 2 = the gut-punch or contrast.
  • Both lines must be able to stand alone as a complete thought.
""",
    },
    {
        "id": "four_liner",
        "label": "4-Liner",
        "emoji": "📝",
        "description": "3–4 short lines. One idea per line.",
        "preview": "── ──────────────────────────────\n── ────────────────────\n── ──────────────────────────\n── ─────────────",
        "prompt_hint": """FORMAT: 4-LINER (STRICT)
HARD RULES:
  • 3 to 4 lines maximum. Each line is short — ideally under 60 characters.
  • One idea per line. No run-on sentences.
  • No paragraphs. No walls of text.
  • The last line should be the sharpest or most surprising.
  • No hashtags. Emojis only if the persona naturally uses them.
""",
    },
    {
        "id": "mid_length",
        "label": "Mid-Length",
        "emoji": "📄",
        "description": "5–8 lines. Room for one paragraph + a kicker.",
        "preview": "── ─────────────────────────────────\n\n── ──────────────────── ─────────── ──────\n── ────── ───── ─────────────\n── ──────────────────────────────────\n\n── ─────────────────────",
        "prompt_hint": """FORMAT: MID-LENGTH
RULES:
  • 5 to 8 lines total.
  • Can have one short paragraph (2–3 sentences) in the middle.
  • Open strong, close strong.
  • Use line breaks intentionally — not just paragraph wrapping.
  • End with a kicker line that stands alone.
  • No hashtags unless the persona uses them. Max 1–2 emojis if persona allows.
""",
    },
    {
        "id": "thread",
        "label": "Thread",
        "emoji": "🧵",
        "description": "Numbered tweets. Hook → Points → Close.",
        "preview": "1/ ──────────────────────────────────\n\n2/ ────── ────────── ─────── ──────\n\n3/ ──────────── ──────────────────\n\n4/ ─────── ──────────────────────\n\n5/ ──────────── ↩",
        "prompt_hint": """FORMAT: THREAD (numbered tweets)
RULES:
  • Output as numbered tweets: 1/ ... 2/ ... 3/ ... etc.
  • Tweet 1 = the HOOK. Must make someone stop scrolling. Bold claim or tension.
  • Tweets 2–4 = expand one point per tweet. Each tweet standalone-readable.
  • Final tweet = close with a CTA, question, or sharp summary line.
  • Total 4–6 tweets. Each tweet max 280 characters.
  • Each tweet separated by a blank line.
  • No "Thread:" prefix. Just start with 1/.
""",
    },
    {
        "id": "ai_decide",
        "label": "Auto (Best Fit)",
        "emoji": "🎯",
        "description": "System picks the right length based on your brief.",
        "preview": "",
        "prompt_hint": """FORMAT: AUTO (BEST FIT)
Choose the format that best serves the brief. Short brief = shorter post. Rich brief with multiple points = consider a thread. 
Default to mid-length if unsure. Never pad to fill space.""",
    },
]


class StyleEngine:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.personas = self._load_data()
        self.tones = TONES
        self.audiences = AUDIENCES
        self.x_formats = X_FORMATS

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

    def get_tones(self) -> list:
        """Return all available tones."""
        return [{"id": t["id"], "label": t["label"], "emoji": t["emoji"], "description": t["description"]} for t in TONES]

    def get_audiences(self) -> list:
        """Return all available target audiences."""
        return [{"id": a["id"], "label": a["label"], "emoji": a["emoji"]} for a in AUDIENCES]

    def get_x_formats(self) -> list:
        """Return all available X post formats."""
        return [{"id": f["id"], "label": f["label"], "emoji": f["emoji"], "description": f["description"], "preview": f["preview"]} for f in X_FORMATS]

    def construct_prompt(
        self,
        persona_id: str,
        platform: str,
        brief: str,
        post_type: Optional[str] = None,
        mood: Optional[str] = None,
        tone: Optional[str] = None,
        target_audience: Optional[str] = None,
        custom_audience: Optional[str] = None,
        x_format: Optional[str] = None,
    ) -> tuple[str, str]:
        p = self.personas.get(persona_id)
        if not p:
            raise ValueError(f"Persona '{persona_id}' not found")

        # ── Extract all sections from the JSON ──────────────────────────────
        persona_info   = p.get("persona", {})
        tone_data      = p.get("tone", {})
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
        tone_overall     = tone_data.get("overall", "")
        tone_descriptors = tone_data.get("descriptors", [])
        tone_never       = tone_data.get("never", [])

        # ── Vocabulary ──────────────────────────────────────────────────────
        sig_phrases   = vocab.get("signature_phrases", [])
        common_words  = vocab.get("common_words", [])
        profanity_lvl = vocab.get("profanity_level", "")
        profanity_ex  = vocab.get("profanity_examples", [])
        number_style  = vocab.get("number_style", "")
        punct_style   = vocab.get("punctuation_style", "")

        # ── Structure ───────────────────────────────────────────────────────
        opening_patterns = structure.get("opening_patterns", [])
        body_patterns    = structure.get("body_patterns", [])
        closing_patterns = structure.get("closing_patterns", [])
        line_break_rules = structure.get("line_break_rules", [])

        # ── Emoji rules ──────────────────────────────────────────────────────
        emoji_freq       = emoji_usage.get("frequency", "")
        emoji_placement  = emoji_usage.get("placement", "")
        emoji_rules_dict = emoji_usage.get("emoji_rules", {})
        emoji_never      = emoji_usage.get("never", [])
        emoji_rules_lines = [f"  • {k}: {v}" for k, v in emoji_rules_dict.items()]

        # ── Post type specific guidance ──────────────────────────────────────
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

        # ── NEW: Writing Tone block ──────────────────────────────────────────
        tone_block = ""
        if tone and tone != "ai_decide":
            matched_tone = next((t for t in TONES if t["id"] == tone), None)
            if matched_tone:
                tone_block = f"""
════════════════════════════════════════════════════════════
WRITING TONE: {matched_tone['label'].upper()}
════════════════════════════════════════════════════════════
{matched_tone['prompt_hint']}
IMPORTANT: The persona voice (vocabulary, structure, signature phrases) stays locked.
This tone is the ANGLE — how the content is delivered, not who is writing.
"""

        # ── NEW: Target Audience block ───────────────────────────────────────
        audience_block = ""
        if target_audience:
            if target_audience == "custom" and custom_audience:
                audience_block = f"""
════════════════════════════════════════════════════════════
TARGET AUDIENCE
════════════════════════════════════════════════════════════
This post is written FOR: {custom_audience}
Adjust vocabulary, references, and assumed knowledge level to match this specific audience.
Don't explain what they already know. Don't use jargon they won't understand.
Write AS the persona, but calibrate the content depth for THIS reader.
"""
            else:
                matched_audience = next((a for a in AUDIENCES if a["id"] == target_audience), None)
                if matched_audience and matched_audience["prompt_hint"]:
                    audience_block = f"""
════════════════════════════════════════════════════════════
TARGET AUDIENCE: {matched_audience['label'].upper()}
════════════════════════════════════════════════════════════
{matched_audience['prompt_hint']}
Calibrate vocabulary, assumed knowledge, and reference points to this specific reader.
"""

        # ── NEW: X Format block ──────────────────────────────────────────────
        x_format_block = ""
        if x_format and platform.upper() in ("X", "TWITTER"):
            matched_format = next((f for f in X_FORMATS if f["id"] == x_format), None)
            if matched_format:
                x_format_block = f"""
════════════════════════════════════════════════════════════
{matched_format['prompt_hint']}════════════════════════════════════════════════════════════
"""

        # ── Recurring motifs ─────────────────────────────────────────────────
        motifs_list = motifs.get("motifs", [])
        motifs_block = ""
        if motifs_list:
            motifs_lines = "\n".join([f"  - {m}" for m in motifs_list])
            motifs_block = f"""
RECURRING MOTIFS (weave in naturally if relevant — never force them):
{motifs_lines}
"""

        # ── Alex vs Zack critical differences ───────────────────────────────
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

        # ── Examples: select up to 10, prioritise matching post type ─────────
        type_examples  = [ex for ex in examples if ex.get("type") == post_type] if post_type else []
        other_examples = [ex for ex in examples if ex.get("type") != post_type]

        selected = type_examples[:3]
        remaining_slots = 10 - len(selected)
        selected += other_examples[:remaining_slots]

        formatted_examples = "\n\n---\n".join([
            f"[EXAMPLE — type: {ex.get('type')}]\n{ex.get('post', '')}"
            for ex in selected
        ])

        # ── Opening / closing patterns ───────────────────────────────────────
        openings_block = "\n".join([f"  • {p}" for p in opening_patterns])
        closings_block = "\n".join([f"  • {p}" for p in closing_patterns])
        body_block     = "\n".join([f"  • {p}" for p in body_patterns])
        breaks_block   = "\n".join([f"  • {r}" for r in line_break_rules])

        # ── Hallucination firewall ────────────────────────────────────────────
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

        # ── Anti-AI Quality Gate (DEEP CLEAN) ────────────────────────────────
        anti_ai_block = """
════════════════════════════════════════════════════════════
ANTI-AI QUALITY GATE — REJECT draft if it contains ANY of these:
════════════════════════════════════════════════════════════
1. BANNED FILLER WORDS / PHRASES:
   ✗ "In today's..." / "In a world where..."
   ✗ "Look no further" / "The truth is" / "The reality is"
   ✗ "It's important to remember" / "One thing I've learned"
   ✗ "Dive deep" / "Delve" / "Unlock" / "Unleash" / "Harness"
   ✗ "Elevate" / "Transform" / "Revolutionize" / "Mastering"
   ✗ "Robust" / "Seamlessly" / "Comprehensive" / "Vital" / "Crucial"
   ✗ "Thilled to announce" / "Excited to share" / "Wanted to take a moment"
   ✗ "Let's connect" / "Drop a comment" / "What are your thoughts?"
   ✗ "Game changer" / "Level up" / "Tapestry" / "Synergy" / "Leverage"
   ✗ "Buckle up" / "Here's the kicker" / "Navigating" / "Empowering"
   ✗ "I'm a big believer in..." / "Success is all about..."

2. BANNED SYMBOLS & FORMATTING:
   ✗ NO ✨ (Sparkles) — absolute ban.
   ✗ NO 🚀 (Rocket) — unless specifically for a milestone announcement.
   ✗ NO 💡 (Lightbulb) — absolute ban for advice.
   ✗ NO starting every line with an emoji.
   ✗ NO starting posts with "Hey guys," "Hi everyone," or "Just shared."
   ✗ NO exclamation marks at the end of every sentence.

3. HUMAN RHYTHM & CONTEXT RULES:
   • NO ELABORATION: If the brief is 5 words, the post should be 5-15 words. Never add "lessons" or "context" not in the brief.
   • Use fragments. "Annoying as hell." is better than "It is very annoying."
   • Use varied sentence lengths. Occasional all-caps for emphasis is fine, but don't overdo it.
   • Write like a voice note, not a blog post.
   • NO hashtags at the end.
════════════════════════════════════════════════════════════
"""

        # ── Output rules from JSON ────────────────────────────────────────────
        output_rules = instructions.get("output_rules", [])
        output_rules_block = "\n".join([f"  - {r}" for r in output_rules])

        # ── System prompt (all identity / rules / examples) ──────────────────
        system_prompt = f"""{system_msg}

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
{diff_block}{motifs_block}{post_type_block}{mood_block}{tone_block}{audience_block}{x_format_block}
════════════════════════════════════════════════════════════
REAL EXAMPLES OF {persona_name.upper()}'S ACTUAL POSTS
════════════════════════════════════════════════════════════
Study these carefully. Match the rhythm, vocabulary, and structure — not just the topic.

{formatted_examples}

{output_rules_block}
{hallucination_firewall}
{anti_ai_block}"""

        # ── User message (just the brief + the trigger to write) ─────────────
        user_message = f"""Here is the brief. Use ONLY these facts — add nothing else:

{brief}

Now write the {platform} post for {persona_name}. Post text only, nothing else:"""

        return system_prompt.strip(), user_message.strip()
