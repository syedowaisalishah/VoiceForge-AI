import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
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

class Persona(BaseModel):
    id: str
    name: str
    description: str

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
            "description": data.get("tone", {}).get("overall", "No description")
        }
        for pid, data in personas_data.items()
    ]

@app.post("/generate")
async def generate_post(request: GenerationRequest):
    try:
        # Construct the persona-driven prompt
        prompt = engine.construct_prompt(
            persona_id=request.persona,
            platform=request.platform,
            brief=request.brief
        )

        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        # 1. Try Gemini (Free Tier) - PRIORITIZED
        if gemini_key and not gemini_key.strip() == "":
            try:
                genai.configure(api_key=gemini_key)
                
                # Force gemini-1.5-flash for the highest free quota
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Disable safety filters to prevent false blocks on business stories
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
                
                response = model.generate_content(prompt, safety_settings=safety_settings)
                return {
                    "persona": request.persona,
                    "platform": request.platform,
                    "content": response.text.strip(),
                    "model": "gemini-1.5-flash"
                }
            except Exception as e:
                print(f"Gemini failed: {e}")
                # If Gemini failed due to quota, we might want to try OpenAI if available
                if not openai_key:
                    raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

        # 2. Try OpenAI fallback
        if openai_key and not openai_key.strip() == "":
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return {
                    "persona": request.persona,
                    "platform": request.platform,
                    "content": response.choices[0].message.content.strip(),
                    "model": "openai-gpt-4o"
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Both AI engines failed. Gemini error: {str(e)}")

        raise HTTPException(status_code=400, detail="No API keys provided")

    except Exception as e:
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
