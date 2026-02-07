from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
import json

app = FastAPI(title="Digital Twin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo twin state (level 1=happy/Focused, 2=mild/Strained, 3=stressed/Overloaded)
_demo_state = {
    "stressBand": "Focused",
    "burnoutValue": 28,
    "avatar": "/avatar-happy.png",
}

LEVEL_PRESETS = {
    1: {"stressBand": "Focused", "burnoutValue": 28, "avatar": "/avatar-happy.png"},
    2: {"stressBand": "Strained", "burnoutValue": 55, "avatar": "/avatar-mildly-stressed.png"},
    3: {"stressBand": "Overloaded", "burnoutValue": 85, "avatar": "/avatar-stressed.png"},
}


class DemoLevelBody(BaseModel):
    level: int = Field(..., ge=1, le=3, description="1=Happy/Focused, 2=Mild/Strained, 3=Stressed/Close to burnout")


@app.get("/state")
async def get_state():
    """Current demo twin state for the frontend (poll this)."""
    return _demo_state.copy()


@app.post("/state")
async def set_state(body: DemoLevelBody):
    """Set demo twin by level: 1=happy+Focused, 2=mild+Strained, 3=stressed+Overloaded. Use from Swagger UI."""
    _demo_state.update(LEVEL_PRESETS[body.level])
    return _demo_state.copy()


@app.get("/api/persona")
async def get_persona():
    """Return the latest persona push payload for frontend consumption.

    Reads `persona_last_push.json` from the repo root and returns it as JSON.
    """
    path = os.path.join(os.getcwd(), "persona_last_push.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="persona_last_push.json not found")
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port)
