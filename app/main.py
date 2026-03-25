from fastapi import FastAPI
from app.api.endpoints import articles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Article API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router, prefix="/articles", tags=["articles"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Article API"}
