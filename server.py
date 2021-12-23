import asyncio
import os

import aiofiles
import diskcache
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()

DISKCACHE_DIRECTORY = os.environ.get('DISKCACHE_DIRECTORY', '/tmp/diskcache')
DISKCACHE_SIZE_LIMIT = eval(os.environ.get('DISKCACHE_SIZE_LIMIT', '4 * (1024 **3)'))
DISKCACHE_DEFAULT_EXPIRE = eval(os.environ.get('DISKCACHE_DEFAULT_EXPIRE', '24 * 60 * 60'))

cache = diskcache.Cache(directory=DISKCACHE_DIRECTORY, size_limit=DISKCACHE_SIZE_LIMIT)


@app.get("/{filename}")
def download_file(filename: str):
    data = cache.get(key=filename, read=True)
    if data is None:
        raise HTTPException(status_code=404)
    return StreamingResponse(data)


@app.put("/{filename}")
async def upload_file(request: Request, filename: str):

    def save_to_cache(tmpfile):
        cache.set(key=filename, value=open(tmpfile, 'rb'), expire=DISKCACHE_DEFAULT_EXPIRE, read=True)

    async with aiofiles.tempfile.NamedTemporaryFile('wb+') as f:
        async for chunk in request.stream():
            await f.write(chunk)
        f.flush()

        await asyncio.to_thread(save_to_cache, f.name)


@app.delete("/{filename}")
def delete_file(filename: str):
    cache.pop(filename)
