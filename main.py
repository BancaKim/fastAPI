from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"),name="static")
app.mount("/img"), StaticFiles(directory="static/img")

@app.get("/")
def read_root():
    return {"message":"Hello, World!"}

@app.get("/include_example")
def include_example(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})