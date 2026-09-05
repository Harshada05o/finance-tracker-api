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
from auth import hash_password, verify_password


def create_user(db: Session, user: schemas.UserCreate):
    hashed = hash_password(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
def create_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(name=category.name, type=category.type, user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_categories(db: Session, user_id: int):
    return db.query(models.Category).filter(models.Category.user_id == user_id).all()

def delete_category(db: Session, category_id: int, user_id: int):
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()
    if category:
        db.delete(category)
        db.commit()
        return True
    return False