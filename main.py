from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal, engine, get_db
from sqlalchemy.orm import Session
import models
from schemas import BookCreate, BookResponse, UserCreate, UserResponse
from sqlalchemy.exc import IntegrityError
from pwdlib import PasswordHash
from auth import get_current_admin, get_current_user, create_acces_token



models.Base.metadata.create_all(bind=engine)
password_hash = PasswordHash.recommended()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=['*'],
    allow_headers=["*"]
)


@app.get("/")
def homepage():
    return "Test"



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
    return get_book_or_404(id, db)

@app.post("/books/{id}/checkout", response_model=BookResponse)
def checkout_book(id: int,
                db: Session=Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    book = get_book_or_404(id, db)
    if not book.is_available:
        raise HTTPException(status_code=409, detail="Book is already checked out")
    book.is_available = False
    db.commit()
    db.refresh(book)
    return book

@app.post("/books/{id}/return", response_model=BookResponse)
def return_book(id: int,
                db: Session=Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    book = get_book_or_404(id, db)
    if book.is_available:
        raise HTTPException(status_code=409, detail="Book is already available")
    book.is_available = True
    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{id}", status_code=204)
def delete_book(id: int,
                db: Session=Depends(get_db),
                admin_user: models.User = Depends(get_current_admin),):
    book = get_book_or_404(id, db)
    db.delete(book)
    db.commit()

@app.put("/books/{id}", response_model=BookResponse)
def update_book(id: int,
                book: BookCreate,
                db: Session=Depends(get_db),
                admin_user: models.User = Depends(get_current_admin)):
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

@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not password_hash.verify(form.password, user.hashed_password):
         raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_acces_token(user.id), "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/books", response_model=BookResponse, status_code=201)
def add_book(book: BookCreate,
            db: Session=Depends(get_db),
            admin_user: models.User = Depends(get_current_admin)):
    new_book = models.Book(**book.model_dump())
    db.add(new_book)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Book with this ISBN already exists")
    db.refresh(new_book)
    return new_book