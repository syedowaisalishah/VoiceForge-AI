from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.core.style_engine import StyleEngine
import google.generativeai as genai

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
        prompt = engine.construct_prompt(request.persona, request.platform, request.brief)
        
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        # 1. Try Gemini (Free Tier) - PRIORITIZED
        if gemini_key and not gemini_key.strip() == "":
            try:
                genai.configure(api_key=gemini_key)
                
                # Try to find an available model dynamically
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else (available_models[0] if available_models else 'gemini-pro')
                
                print(f"Using Gemini model: {target_model}")
                model = genai.GenerativeModel(target_model)
                response = model.generate_content(prompt)
                return {
                    "persona": request.persona,
                    "platform": request.platform,
                    "content": response.text.strip(),
                    "model": f"gemini ({target_model})"
                }
            except Exception as e:
                print(f"Gemini failed, trying OpenAI: {e}")

        # 2. Try OpenAI if Gemini fails or is not provided
        if openai_key and not openai_key.strip() == "":
            try:
                import openai # Ensure openai is imported inside if needed or global
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
                    "model": "openai"
                }
            except Exception as e:
                print(f"OpenAI also failed: {e}")

        # 3. Mock Response if no keys work
        return {
            "persona": request.persona,
            "platform": request.platform,
            "content": f"[MOCK RESPONSE] {request.persona} on {request.platform}: {request.brief}. (Please add credits to OpenAI or use a free Gemini API key)",
            "prompt_used": prompt
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
