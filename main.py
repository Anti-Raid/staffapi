from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from s3 import create_app
import dotenv

dotenv.load_dotenv()

app = FastAPI()
app.mount("/s3", WSGIMiddleware(create_app()))