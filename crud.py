from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas


def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(
        user_id=user_id,
        category_id=transaction.category_id,
        amount=transaction.amount,
        note=transaction.note,
        date=transaction.date,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def get_transactions(db: Session, user_id: int):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()


def get_summary(db: Session, user_id: int):
    income = (
        db.query(func.sum(models.Transaction.amount))
        .join(models.Category)
        .filter(models.Transaction.user_id == user_id, models.Category.type == "income")
        .scalar() or 0
    )
    expense = (
        db.query(func.sum(models.Transaction.amount))
        .join(models.Category)
        .filter(models.Transaction.user_id == user_id, models.Category.type == "expense")
        .scalar() or 0
    )
    return {
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense,
    }