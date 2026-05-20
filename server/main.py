import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.core.style_engine import StyleEngine

load_dotenv()

app = FastAPI(title="VoiceForge AI Backend")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Style Engine
DATA_DIR = os.path.join(os.path.dirname(__file__), "app", "data")
engine = StyleEngine(DATA_DIR)


class GenerationRequest(BaseModel):
    persona: str
    platform: str
    brief: str
    post_type: Optional[str] = None
    mood: Optional[str] = None
    tone: Optional[str] = None
    target_audience: Optional[str] = None
    custom_audience: Optional[str] = None
    x_format: Optional[str] = None


class Persona(BaseModel):
    id: str
    name: str
    description: str


class PostType(BaseModel):
    id: str
    label: str
    description: str


class ToneOption(BaseModel):
    id: str
    label: str
    emoji: str
    description: str


class AudienceOption(BaseModel):
    id: str
    label: str
    emoji: str


class XFormatOption(BaseModel):
    id: str
    label: str
    emoji: str
    description: str
    preview: str


@app.get("/")
async def root():
    return {"message": "VoiceForge AI API is running"}


@app.get("/personas", response_model=List[Persona])
async def get_personas():
    personas_data = engine.personas
    return [
        {
            "id": pid,
            "name": data.get("persona", {}).get("name", pid.capitalize()),
            "description": data.get("persona", {}).get(
                "voice_summary",
                data.get("tone", {}).get("overall", "No description")
            )
        }
        for pid, data in personas_data.items()
    ]


@app.get("/post-types/{persona_id}", response_model=List[PostType])
async def get_post_types(persona_id: str):
    """Return available post types for a given persona."""
    if persona_id not in engine.personas:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")
    return engine.get_post_types(persona_id)


@app.get("/tones", response_model=List[ToneOption])
async def get_tones():
    """Return all available writing tones."""
    return engine.get_tones()


@app.get("/audiences", response_model=List[AudienceOption])
async def get_audiences():
    """Return all available target audiences."""
    return engine.get_audiences()


@app.get("/x-formats", response_model=List[XFormatOption])
async def get_x_formats():
    """Return all available X post formats."""
    return engine.get_x_formats()


@app.post("/generate")
async def generate_post(request: GenerationRequest):
    try:
        system_prompt, user_message = engine.construct_prompt(
            persona_id=request.persona,
            platform=request.platform,
            brief=request.brief,
            tone=request.tone,
            target_audience=request.target_audience,
            custom_audience=request.custom_audience,
            x_format=request.x_format,
        )
        
        print(f"DEBUG: Constructing prompt for {request.persona}...")

        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        # ── Gemini ─────────────────────────────────────────────────────────
        if gemini_key and gemini_key.strip():
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=gemini_key)
                
                available = []
                try:
                    available = [m.name for m in client.models.list()]
                    print(f"DEBUG: Available models: {available}")
                except Exception as e:
                    print(f"Model discovery failed: {e}")

                priority_models = [
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-latest",
                    "gemini-1.5-flash-8b",
                    "gemini-flash-latest",
                    "gemini-2.0-flash",
                ]

                target_model = "gemini-1.5-flash"
                for candidate in priority_models:
                    full_name = f"models/{candidate}"
                    if full_name in available or candidate in available:
                        target_model = candidate
                        break

                print(f"DEBUG: Attempting generation with: {target_model}")

                config = types.GenerateContentConfig(
                    # System instruction keeps rules fully separate from the user turn
                    system_instruction=system_prompt,
                    temperature=0.65,
                    top_p=0.92,
                    top_k=40,
                    safety_settings=[
                        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT",        threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH",        threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT",  threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT",  threshold="BLOCK_NONE"),
                    ]
                )

                # user_message is the ONLY thing in contents — clean turn boundary
                response = client.models.generate_content(
                    model=target_model,
                    contents=user_message,
                    config=config,
                )

                return {
                    "persona": request.persona,
                    "platform": request.platform,
                    "post_type": request.post_type,
                    "tone": request.tone,
                    "target_audience": request.target_audience,
                    "x_format": request.x_format,
                    "content": response.text.strip(),
                    "model": target_model,
                }

            except Exception as e:
                print(f"Gemini failed: {e}")
                if not openai_key:
                    raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

        # ── OpenAI fallback ───────────────────────────────────────────────
        if openai_key and openai_key.strip():
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_message},
                ],
                temperature=0.65,
                top_p=0.92,
            )
            return {
                "persona": request.persona,
                "platform": request.platform,
                "post_type": request.post_type,
                "tone": request.tone,
                "target_audience": request.target_audience,
                "x_format": request.x_format,
                "content": response.choices[0].message.content.strip(),
                "model": "openai-gpt-4o",
            }

        raise HTTPException(
            status_code=400,
            detail="No API keys configured. Set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."
        )


    except HTTPException:
        raise
    except Exception as e:
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
