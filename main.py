from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from database import SessionLocal, engine, Base
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Finance Tracker")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Finance Tracker API is running"}
import crud


@app.post("/transactions", response_model=schemas.TransactionOut)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # Hardcoding user_id=1 for now since we haven't built login/auth yet
    return crud.create_transaction(db, transaction, user_id=1)


@app.get("/transactions", response_model=list[schemas.TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    return crud.get_transactions(db, user_id=1)


@app.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return crud.get_summary(db, user_id=1)
