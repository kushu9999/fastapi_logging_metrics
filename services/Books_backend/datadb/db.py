from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table


DATABASE_URL = "sqlite:///./test.db"

# Database setup
engine = create_engine(DATABASE_URL)
metadata = MetaData()

booksdb = Table(
    "books",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("author", String),
    Column("published_year", Integer),
)

metadata.create_all(bind=engine)
