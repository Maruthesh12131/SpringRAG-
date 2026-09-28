# Spring Boot RAG Assistant — Frontend

React + Vite chat UI for the Spring Boot RAG API (`POST /api/ask`, `GET /api/health`).

## Run locally

Start the FastAPI service (:8000) and Spring Boot (:8080) first, then:

```bash
cd frontend
cp .env.example .env   # first time only
npm install
npm run dev            # http://localhost:5173
```

## Configuration

| Variable            | Used by            | Default                 | Purpose |
|---------------------|--------------------|-------------------------|---------|
| `VITE_BACKEND_URL`  | Vite dev proxy     | `http://localhost:8080` | Where `/api/*` is proxied during `npm run dev`. |
| `VITE_API_BASE_URL` | Browser (built in) | empty (same origin)     | Base URL the browser calls. Leave empty when the UI and API share an origin. |

In development the browser only talks to `localhost:5173`, and Vite forwards `/api/*`
to Spring Boot, so no CORS configuration is needed on the backend.

## Production build

```bash
npm run build          # outputs static files to dist/
```

Serve `dist/` from the same origin as the API (e.g. copy it into Spring Boot's
`src/main/resources/static/`, or put both behind one reverse proxy). If you instead
serve it from a different origin and set `VITE_API_BASE_URL`, the Spring Boot app must
allow that origin via CORS.
