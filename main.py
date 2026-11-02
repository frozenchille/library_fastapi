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

@app.get("/books/{id}", response_model=BookResponse,)
def get_book_by_id(id: int, db: Session=Depends(get_db)):
    db_product = db.query(models.Book).filter(models.Book.id == id).first()
    if db_product and db_product.is_available==True:
         return db_product
    raise HTTPException(status_code=404, detail="Book not found or currently not available")

@app.post("/books", response_model=BookResponse)
def add_book(book: BookCreate, db: Session=Depends(get_db)):
    new_book = models.Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book