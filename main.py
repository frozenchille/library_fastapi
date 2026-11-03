from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
from sqlalchemy.orm import Session
import models
from schemas import BookCreate, BookResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=['*']
)



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
    db_products = db.query(models.Book).all()
    return db_products

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

@app.post("/books", response_model=BookResponse)
def add_book(book: BookCreate, db: Session=Depends(get_db)):
    new_book = models.Book(**book.model_dump())
    db.add(new_book)
    db.commit()
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
    raise HTTPException(status_code=200, detail="Book was deleted succesfully")

@app.put("/books/{id}", response_model=BookResponse)
def update_book(id: int, book: BookCreate, db: Session=Depends(get_db)):
    db_book = get_book_or_404(id, db)
    db_book.author = book.author
    db_book.title = book.title
    db_book.isbn = book.isbn
    db.commit()
    db.refresh(db_book)
    return db_book
    
     