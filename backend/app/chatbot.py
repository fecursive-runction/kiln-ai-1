import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from .data_loader import combined_data

# (Configuration and ChatRequest model are the same)
load_dotenv()
router = APIRouter()
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini AI model configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini AI: {e}")
    model = None
class ChatRequest(BaseModel):
    message: str


@router.post("/ai/chat")
async def get_ai_response(request: ChatRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Gemini AI model is not configured.")

    try:
        if not combined_data:
            latest_data_summary = "Plant data is not yet available. Please try again in a moment."
        else:
            # Use list slicing instead of .tail() and .iloc()
            recent_data = combined_data[-20:]
            latest_data = recent_data[-1]
            # Manually calculate average instead of .mean()
            avg_spc = sum(d['spc'] for d in recent_data) / len(recent_data)
            
            latest_data_summary = f"""
            - Specific Power Consumption (SPC): The current reading is {latest_data['spc']:.2f} kWh/t, compared to a recent average of {avg_spc:.2f} kWh/t.
            - Thermal Substitution Rate (TSR): Currently at {latest_data['tsr']:.2f}%.
            - Clinker Quality Index: Currently at {latest_data['clinker_quality']:.2f}%.
            """

        # (Prompt remains the same)
        prompt = f"""
        **//-- MASTER PROMPT: AI CO-PILOT PERSONA --//**
        **YOUR PERSONA:** You are "Cement-AI," a world-class AI co-pilot for a cement plant operator...
        **CURRENT PLANT DATA CONTEXT:**
        {latest_data_summary}
        **USER'S MESSAGE:**
        "{request.message}"
        **YOUR RESPONSE:**
        """
        response = await model.generate_content_async(prompt)
        return {"reply": response.text}

    except Exception as e:
        print(f"Error during AI generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
