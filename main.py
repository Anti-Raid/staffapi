from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from s3 import start_s3_proc
import dotenv
import threading

dotenv.load_dotenv(override=True)

app = FastAPI()

threading.Thread(target=start_s3_proc).start()