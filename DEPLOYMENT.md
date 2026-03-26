# Deployment

## Frontend on Vercel

Project root:
`frontend`

Required environment variables:

```env
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

Build settings if needed:

- Install Command: `npm install`
- Build Command: `npm run build`
- Output Directory: `dist`

## Backend on Render

Render can deploy from [render.yaml](/D:/DodgeAI/render.yaml) at the repo root.
The backend must run from the repository root because the app imports `backend.main` as a package.

Environment variables:

```env
GEMINI_API_KEY=your_real_key
GEMINI_MODEL=gemini-2.0-flash
DATABASE_URL=sqlite:///./backend/app.db
DATA_DIR=./data
```

Start command:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## Dataset

Current backend startup loads the dataset from `DATA_DIR` and rebuilds SQLite on startup.
That means Render needs access to the `data/` directory at runtime.

Recommended options:

1. Keep `data/` in the repository if the dataset size is small enough for git and Render builds.
2. If the dataset is too large or sensitive, move it to external storage and update `init_db.py` to download or mount it before startup.

If `data/` is not present on Render, the backend will start, but the graph and query data will be empty.
