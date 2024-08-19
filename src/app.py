from fastapi import FastAPI

from kb import kb_router

app = FastAPI(title='WeYon AI Open Platform', version='0.1.0')

app.include_router(kb_router.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
