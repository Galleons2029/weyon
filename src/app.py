from fastapi import FastAPI

from router import file

app = FastAPI(title='WeYon AI Open Platform', version='0.1.0')

app.include_router(file.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
