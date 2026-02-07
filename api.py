from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
import json

app = FastAPI(title="Digital Twin API")


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
