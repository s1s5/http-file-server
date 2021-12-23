import asyncio

import aiofiles
import diskcache
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()
cache = diskcache.Cache(directory='/tmp/diskcache', size_limit=4 * (1024 ** 3))
DEFAULT_EXPIRE = 24 * 60 * 60


@app.get("/{filename}")
def download_file(filename: str):
    data = cache.get(key=filename, read=True)
    if data is None:
        raise HTTPException(status_code=404)
    return StreamingResponse(data)


@app.put("/{filename}")
async def upload_file(request: Request, filename: str):

    def save_to_cache(tmpfile):
        cache.set(key=filename, value=open(tmpfile, 'rb'), expire=DEFAULT_EXPIRE, read=True)

    async with aiofiles.tempfile.NamedTemporaryFile('wb+') as f:
        async for chunk in request.stream():
            await f.write(chunk)
        f.flush()

        await asyncio.to_thread(save_to_cache, f.name)
