import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from .data_loader import combined_data

# (Configuration and OptimizerRequest model are the same)
load_dotenv()
router = APIRouter()
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini AI model for Optimizer configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini AI for Optimizer: {e}")
    model = None
class OptimizerRequest(BaseModel):
    targetSPC: float
    targetQuality: float
    maxTSR: float


@router.post("/ai/optimize")
async def get_optimization_plan(request: OptimizerRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Gemini AI model is not configured.")

    try:
        if not combined_data:
             raise HTTPException(status_code=503, detail="Plant data is not yet available.")
        
        # Get the most recent row using list slicing
        latest_data = combined_data[-1]

        # (Prompt remains the same)
        prompt = f"""
        **ROLE:** You are a master Process Optimization Engineer for a cement plant...
        **CURRENT PLANT STATE (LIVE DATA):**
        - Specific Power Consumption (SPC): {latest_data['spc']:.2f} kWh/t
        - Clinker Quality Index: {latest_data['clinker_quality']:.2f}%
        - Thermal Substitution Rate (TSR): {latest_data['tsr']:.2f}%
        **OPERATOR'S TARGETS:**
        - Target SPC: {request.targetSPC} kWh/t
        - Target Clinker Quality: {request.targetQuality}%
        - Maximum allowable TSR: {request.maxTSR}%
        **YOUR RECOMMENDATION:**
        ...
        """
        response = await model.generate_content_async(prompt)
        return {"recommendation": response.text}

    except Exception as e:
        print(f"Error during AI optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))
