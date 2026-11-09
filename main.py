from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import models
from schemas import BookCreate, BookResponse, UserCreate, UserResponse
from sqlalchemy.exc import IntegrityError
from pwdlib import PasswordHash
from dotenv import load_dotenv
import datetime
from datetime import timedelta, timezone
import jwt
import os

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=['*']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
password_hash = PasswordHash.recommended()


SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.get("/")
def homepage():
    return "Test"


def get_db():
    db = SessionLocal()
    try:
            yield db
    finally:
            db.close()


@app.get("/books", response_model=list[BookResponse])
def get_all_books(db: Session=Depends(get_db)):
    db_books = db.query(models.Book).all()
    return db_books

def get_book_or_404(id: int, db: Session):
    book = db.query(models.Book).filter(models.Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/books/{id}", response_model=BookResponse)
def get_book_by_id(id: int, db: Session=Depends(get_db)):
    book = get_book_or_404(id, db)
    if not book.is_available:
        raise HTTPException(status_code=409, detail="Book is currently checked out")
    return book

@app.post("/books", response_model=BookResponse, status_code=201)
def add_book(book: BookCreate, db: Session=Depends(get_db)):
    new_book = models.Book(**book.model_dump())
    db.add(new_book)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Book with this ISBN already exists")
    db.refresh(new_book)
    return new_book

@app.post("/books/{id}/checkout", response_model=BookResponse)
def checkout_book(id: int, db: Session=Depends(get_db)):
    book = get_book_or_404(id, db)
    if not book.is_available:
        raise HTTPException(status_code=409, detail="Book is already checked out")
    book.is_available = False
    db.commit()
    db.refresh(book)
    return book

@app.post("/books/{id}/return", response_model=BookResponse)
def return_book(id: int, db: Session=Depends(get_db)):
    book = get_book_or_404(id, db)
    if book.is_available:
        raise HTTPException(status_code=409, detail="Book is already available")
    book.is_available = True
    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{id}")
def delete_book(id: int, db: Session=Depends(get_db)):
    book = get_book_or_404(id, db)
    db.delete(book)
    db.commit()

@app.put("/books/{id}", response_model=BookResponse)
def update_book(id: int, book: BookCreate, db: Session=Depends(get_db)):
    db_book = get_book_or_404(id, db)
    db_book.author = book.author
    db_book.title = book.title
    db_book.isbn = book.isbn
    try:
            db.commit()
    except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Book with this ISBN already exists")
    db.refresh(db_book)
    return db_book


@app.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate, db: Session=Depends(get_db)):
    hashed_password = password_hash.hash(user.password)
    new_user = models.User(email = user.email, hashed_password = hashed_password)
    db.add(new_user)
    try:
         db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    db.refresh(new_user)
    return new_user

def create_acces_token(user_id: int) -> str:
    payload = {"sub": str(user_id),
                "exp": (datetime.datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITM)

@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not password_hash.verify(form.password, user.hashed_password):
         raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_acces_token(user.id), "token_type": "bearer"}
    