import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api import book_crud
import sentry_sdk

sentry_sdk.init(
    dsn="https://1e97ad0c1e931e2dbaf381522998d675@o4506762393419776.ingest.sentry.io/4506762394992640",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


# creating fastapi
app = FastAPI(title="Book Application")

# connect router to main api
app.include_router(book_crud.router)

# adding middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # add your domains here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def measure_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    # time.sleep(1)
    end_time = time.time()

    total_time = end_time - start_time
    response.headers["X-Total-Request-Time"] = str(round(total_time, 3))

    return response

# homeurl


@app.get("/", tags=["Home"])
def index():
    return {
        "Message": "Hello, Welcome to Books API, goto /docs for more information"
    }
