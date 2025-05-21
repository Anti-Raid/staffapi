from enum import Enum
from fastapi import FastAPI, Request, BackgroundTasks
import dotenv
import boto3
from secrets import token_hex

results = {}
def setup_task() -> str:
    id = token_hex()
    results[id] = {"output": [], "status": "pending"}
    return id

def add_task_output(id: str, output):
    if results.get(id) is None:
        return
    results[id]["output"].append(output)

def set_task_status(id: str, status: str):
    if results.get(id) is None:
        return
    results[id]["status"] = status

dotenv.load_dotenv(override=True)

app = FastAPI()
s3 = boto3.resource('s3')

@app.get("/s3/buckets")
def get_bucket_list():
    names = []
    for bucket in s3.buckets.all():
        if not bucket.name.startswith("antiraid.guild."):
            continue
        names.append(bucket.name)
    return {
        "names": names,
        "count": len(names)
    }

class FindMode(Enum):
    STARTS_WITH = "startswith"
    IN = "in"
    ENDS_WITH = "endswith"


@app.post("/s3/buckets/findData")
async def find_files_with_data(request: Request, background_tasks: BackgroundTasks, mode: FindMode, len: int | None = None, delete_matched: bool | None = None):
    """Warning: this OP is extremely slow"""
    frag = await request.body()
    id = setup_task()
    background_tasks.add_task(find_data_op, mode, frag, id, len, delete_matched)
    return {"tid": id}

def find_data_op(mode: FindMode, frag: bytes, id: str, length: int | None, delete_matched: bool | None):
    files = []
    add_task_output(id, files)
    nb = 0
    for bucket in s3.buckets.all():
        if length and nb > length:
            break
        if not bucket.name.startswith("antiraid.guild."):
            continue

        print(bucket)
        
        for file in bucket.objects.all():
            amt = None
            if mode == FindMode.STARTS_WITH:
                amt = len(frag) + 1 # No need to read every file in a startswith op
            body = file.get()['Body'].read(amt=amt)

            matched = False
            if mode == FindMode.STARTS_WITH and body.startswith(frag):
                matched = True
            if mode == FindMode.IN and frag in body:
                matched = True
            if mode == FindMode.ENDS_WITH and body.endswith(frag):
                matched = True
            
            if matched:
                files.append({"key": file.key, "bucket_name": file.bucket_name})
                if delete_matched:
                    file.delete()

        nb+=1
        set_task_status(id, f"pending_{nb}")
    set_task_status(id, "done")
    return files

@app.get("/tasks/{id}")
async def get_task_output(id: str):
    if results.get(id) is None:
        return None
    return results[id]