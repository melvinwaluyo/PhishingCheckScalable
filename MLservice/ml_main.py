from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# Load models and vectorizers
model_phishing = joblib.load("./ml_model/svm_model_phishing.joblib")
vectorizer_phishing = joblib.load("./ml_model/svm_vectorizer_phishing.joblib")

class TextRequest(BaseModel):
    text: str

@app.post("/model_predict")
def predict_phishing_model(request: TextRequest):
    if not request.text:
        return {"error": "No text provided"}

    text_vectorized = vectorizer_phishing.transform([request.text])
    prediction = model_phishing.predict(text_vectorized)
    prediction_proba = model_phishing.predict_proba(text_vectorized)
    result = "Phishing" if prediction[0] == 1 else "Not Phishing"
    accuracy = float(max(prediction_proba[0]))

    return {"prediction": result, "accuracy": accuracy, "details": prediction_proba.tolist()}