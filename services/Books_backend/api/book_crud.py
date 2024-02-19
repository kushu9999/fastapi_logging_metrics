import time
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from datadb.models import Book, BookCreate
from databases import Database
from typing import List
from datadb.db import booksdb, DATABASE_URL
from utilities.utility_functions import log_to_cloudwatch
from logs.logging import add_logs_loki
router = APIRouter()

# Dependency to get the database session


def get_database():
    db = Database(DATABASE_URL)
    return db

# Dependency to get the database session


async def get_db(db: Database = Depends(get_database)):
    try:
        yield db
    finally:
        await db.disconnect()


def logs_to_cloudwatch_background(log_message):
    print("received here")
    start = time.time()
    log_to_cloudwatch(log_message)
    end = time.time() - start
    print(f"logs sent sucessfully on cloudwatch in {end}s.")


# CRUD operations
@router.post("/books/", response_model=Book)
async def create_book(book: BookCreate, db: Database = Depends(get_db)):
    query = booksdb.insert().values(title=book.title, author=book.author, published_year=book.published_year)
    book_id = await db.execute(query)
    return {**book.dict(), "id": book_id}


@router.get("/books/", response_model=List[Book])
async def read_books(request: Request, start: int = 0, end: int = 10, db: Database = Depends(get_db)):

    try:
        query = booksdb.select().offset(start).limit(end)
        result = await db.fetch_all(query)
        log_message = f"Ip: {request.client.host}, start_index: {start}, stop_index: {end}, result: {result}"
        log_to_cloudwatch(log_message)
        add_logs_loki(log_message)
        return result

    except Exception as e:
        log_message = {"error": str(e)}
        add_logs_loki(log_message,error=True)
        return JSONResponse(content=log_message, status_code=500)


@router.get("/books2/", response_model=List[Book])
async def read_books2(background_tasks: BackgroundTasks, request: Request, start: int = 0, end: int = 10, db: Database = Depends(get_db)):

    try:
        query = booksdb.select().offset(start).limit(end)
        result = await db.fetch_all(query)
        log_message = f"Ip: {request.client.host}, start_index: {start}, stop_index: {end}, result: {result}"
        background_tasks.add_task(log_to_cloudwatch, log_message)
        add_logs_loki(log_message)
        return result

    except Exception as e:
        log_message = {"error": str(e)}
        add_logs_loki(log_message,error=True)
        return JSONResponse(content=log_message, status_code=500)


@router.get("/books3/", response_model=List[Book])
async def read_books3(background_tasks: BackgroundTasks, request: Request, start: int = 0, end: int = 10, db: Database = Depends(get_db)):

    try:
        query = booksdb.select().offset(start).limit(end)
        result = await db.fetch_all(query)
        add_logs_loki(result)
        return result

    except Exception as e:
        log_message = {"error": str(e)}
        add_logs_loki(log_message,error=True)
        return JSONResponse(content=log_message, status_code=500)


@router.get("/books/{book_id}", response_model=Book)
async def read_book(book_id: int, db: Database = Depends(get_db)):
    query = booksdb.select().where(booksdb.c.id == book_id)
    result = await db.fetch_one(query)
    if result is None:
        add_logs_loki(log_message=f"Book not found with id: {book_id}",error=True)
        raise HTTPException(status_code=404, detail=f"Book not found with id: {book_id}")
    else:
        add_logs_loki(log_message=result)
    return result


@router.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, book: BookCreate, db: Database = Depends(get_db)):
    query = booksdb.update().where(booksdb.c.id == book_id).values(**book.dict())
    updated_rows = await db.execute(query)
    if updated_rows == 0:
        add_logs_loki(log_message=f"Book not found with id: {book_id}",error=True)
        raise HTTPException(status_code=404, detail=f"Book not found with id: {book_id}")
    else:
        add_logs_loki(log_message=updated_rows)
    return {**book.dict(), "id": book_id}


@router.delete("/books/{book_id}", response_model=Book)
async def delete_book(book_id: int, db: Database = Depends(get_db)):
    query = booksdb.delete().where(booksdb.c.id == book_id)
    deleted_rows = await db.execute(query)
    if deleted_rows == 0:
        add_logs_loki(log_message=f"Book not found with id: {book_id}",error=True)
        raise HTTPException(status_code=404, detail=f"Book not found with id: {book_id}")
    else:
        add_logs_loki(log_message=deleted_rows)
    return {"id": book_id}


@router.get("/sentry-debug")
async def trigger_error():
    try:
        division_by_zero = 1 / 0
        return division_by_zero

    except Exception as e:
        add_logs_loki(log_message=f"Error {e}",error=True)
