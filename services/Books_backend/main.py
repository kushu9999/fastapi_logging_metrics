import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api import book_crud
import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator
from logs.logging import add_logs_loki
import logging, uvicorn

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

@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    console_formatter = uvicorn.logging.ColourizedFormatter(
        "{asctime} {levelprefix} : {message}",
        style="{", use_colors=True)
    logger.handlers[0].setFormatter(console_formatter)

@app.middleware("http")
async def measure_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    # time.sleep(1)
    end_time = time.time()

    total_time = end_time - start_time
    response.headers["X-Total-Request-Time"] = str(round(total_time, 3))

    return response


@app.get("/", tags=["Home"])
def index():
    log_data = "Hello, Welcome to Books API, goto /docs for more information"
    add_logs_loki(log_data)
    return {
        "Message": "Hello, Welcome to Books API, goto /docs for more information"
    }

Instrumentator().instrument(app).expose(app)
