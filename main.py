from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from database import SessionLocal, engine, Base
import models
import schemas
import crud
from auth import create_access_token, decode_access_token
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Finance Tracker")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    username = payload.get("sub")
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/")
def root():
    return {"message": "Finance Tracker API is running"}


@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    return crud.create_user(db, user)


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/transactions", response_model=schemas.TransactionOut)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_transaction(db, transaction, user_id=current_user.id)


@app.get("/transactions", response_model=list[schemas.TransactionOut])
def list_transactions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_transactions(db, user_id=current_user.id)


@app.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_summary(db, user_id=current_user.id)

@app.post("/categories", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_category(db, category, user_id=current_user.id)


@app.get("/categories", response_model=list[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_categories(db, user_id=current_user.id)

@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    success = crud.delete_category(db, category_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}

@app.get("/analytics/spending-chart")
def spending_chart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    transactions = crud.get_transactions(db, user_id=current_user.id)

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    data = [{
        "category": t.category.name,
        "type": t.category.type,
        "amount": float(t.amount)
    } for t in transactions]
    df = pd.DataFrame(data)

    expenses = df[df["type"] == "expense"]
    category_totals = expenses.groupby("category")["amount"].sum()

    if category_totals.empty:
        raise HTTPException(status_code=404, detail="No expense data to chart")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(category_totals.index, category_totals.values, color="#4C9AFF")
    ax.set_title("Spending by Category")
    ax.set_ylabel("Amount")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")