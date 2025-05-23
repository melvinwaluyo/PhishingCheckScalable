# backend/app/routes/predict.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session
from app.models.model_phishingresult import PhishingResult
from app.db import get_db
from app.cache import get_redis_connection
import redis
import json
import os # <-- Make sure this is imported

class TextRequest(BaseModel):
    text: str

predict_router = APIRouter(tags=["Predict"])

# --- THIS IS THE CRITICAL CHANGE ---
# Get ML Service URL from Environment. If not found, raise an error.
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")
if not ML_SERVICE_URL:
    print("--- !!! FATAL ERROR: ML_SERVICE_URL environment variable not set !!! ---")
    raise ValueError("FATAL ERROR: ML_SERVICE_URL environment variable not set.")

print(f"--- !!! ML SERVICE URL BEING USED: {ML_SERVICE_URL} !!! ---")
# --- END CRITICAL CHANGE ---


@predict_router.post("/")
def predict_phishing(
    request: TextRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_connection)
):
    if not request.text:
        raise HTTPException(status_code=400, detail="No text provided")

    cache_key = f"phishing_check:{request.text}"
    cached_result = None
    is_cached = False
    phishing_result_id = None

    # 1. Check Cache
    if redis_client:
        try:
            cached_value = redis_client.get(cache_key)
            if cached_value:
                print("Cache HIT!")
                cached_result = json.loads(cached_value)
                is_cached = True
        except Exception as e:
            print(f"Redis GET failed: {e}")

    if is_cached:
        result = cached_result.get("prediction")
        accuracy = cached_result.get("accuracy")
        existing_db_entry = db.query(PhishingResult).filter(PhishingResult.textInput == request.text).first()
        if existing_db_entry:
            phishing_result_id = existing_db_entry.phishingresultID

    else:
        print("Cache MISS! Calling ML Service...")
        # 2. If Cache MISS -> Call ML Service
        try:
            print(f"--- !!! CALLING: {ML_SERVICE_URL} !!! ---") # Debug print
            # Use the ML_SERVICE_URL variable which now comes from the environment
            response = requests.post(ML_SERVICE_URL, json={"text": request.text})
            response.raise_for_status()
            ml_data = response.json()

            result = ml_data.get("prediction")
            accuracy = ml_data.get("accuracy")

            if result is None or accuracy is None:
                raise HTTPException(status_code=500, detail="Invalid response from ML service")

            # 3. Store in Cache
            if redis_client:
                try:
                    redis_client.setex(cache_key, 3600, json.dumps({"prediction": result, "accuracy": accuracy}))
                except Exception as e:
                    print(f"Redis SET failed: {e}")

            # 4. Check DB and Save
            existing_db_entry = db.query(PhishingResult).filter(PhishingResult.textInput == request.text).first()
            if existing_db_entry:
                phishing_result_id = existing_db_entry.phishingresultID
            else:
                phishing_result = PhishingResult(textInput=request.text, accuracy=accuracy, verdict=result)
                db.add(phishing_result)
                db.commit()
                db.refresh(phishing_result)
                phishing_result_id = phishing_result.phishingresultID

        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"ML service unavailable: {e}")

    # 5. Return result
    return {
        "prediction": result,
        "accuracy": accuracy,
        "phishingresultID": phishing_result_id,
        "cached": is_cached
    }