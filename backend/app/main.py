import sys
from pathlib import Path

from fastapi import FastAPI

if __package__ in {None, ''}:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    from backend.app.api.router import api_router
    from backend.app.core.security import configure_cors
except ModuleNotFoundError:  # pragma: no cover - compatibility when run from backend package path
    from app.api.router import api_router
    from app.core.security import configure_cors

app = FastAPI(title='AI MovieLens API', version='1.0.0')
configure_cors(app)
app.include_router(api_router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('backend.app.main:app', host='0.0.0.0', port=8000, reload=True)
