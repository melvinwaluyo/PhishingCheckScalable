from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import predict_router
from app.db import get_db, Base, engine
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_credentials=True,
    allow_headers=['*']
)

app.include_router(predict_router, prefix="/api/predict")