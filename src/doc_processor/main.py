from fastapi import FastAPI

from doc_processor.api.v1.router import api_router

app = FastAPI()
app.include_router(api_router)
