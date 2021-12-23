# http-file-server
simple http file server

- `curl -T a.jpg http://localhost:8000/a.jpg`
- `curl http://localhost:8000/a.jpg --output /tmp/a.jpg`
- `curl -X DELETE http://localhost:8000/a.jpg`

## environment variables
- DISKCACHE_DIRECTORY
- DISKCACHE_SIZE_LIMIT
- DISKCACHE_DEFAULT_EXPIRE
