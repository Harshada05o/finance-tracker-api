# Personal Finance Tracker API

A backend API for tracking personal income and expenses, built with FastAPI and PostgreSQL.

## Features
- Add income/expense transactions with categories
- List all transactions
- View income/expense summary with net balance

## Tech Stack
- Python, FastAPI, SQLAlchemy, PostgreSQL, Pydantic

## Setup
1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it and run `pip install -r requirements.txt`
4. Set up a PostgreSQL database named `finance_tracker`
5. Update the connection string in `database.py`
6. Run `python main.py` once to create tables
7. Run `uvicorn main:app --reload`
8. Visit `http://127.0.0.1:8000/docs`

## Status
Basic version complete (CRUD + summary). JWT auth, Redis caching, and Docker support planned next.