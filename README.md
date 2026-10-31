# Containerised Library Book Tracker
Flask + SQLite app to track issued library books.

Run: docker run -p 5000:5000 -v lib-data:/data <image>

## Build and run
```
docker build -t <user>/library-tracker:v1-full -f Dockerfile.full .
docker build -t <user>/library-tracker:v2-slim -f Dockerfile .
docker run -p 5000:5000 -v lib-data:/data <user>/library-tracker:v2-slim
```
Open http://localhost:5000. Tests: `pip install flask pytest && pytest`.
See COMPARISON.md for the image comparison and justification.
