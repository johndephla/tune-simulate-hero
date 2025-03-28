
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title="Suno.ai Automation API")

class GenerateRequest(BaseModel):
    prompt: str
    download: bool = False

@app.get("/")
async def root():
    return {"status": "ok", "message": "Suno.ai Automation API is running"}

@app.post("/generate")
async def generate_song(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate a song on Suno.ai with the given prompt
    """
    logger.info(f"Received generation request with prompt: {request.prompt}")
    
    # Get automation instance from app state
    automation = app.state.automation
    
    if not automation:
        raise HTTPException(status_code=500, detail="Automation not initialized")
    
    # Generate song
    result = automation.generate_song(request.prompt)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate song"))
    
    # Download the song if requested
    if request.download:
        download_result = automation.download_song(result.get("url"))
        if download_result.get("success"):
            result["file_path"] = download_result.get("file_path")
        else:
            logger.warning(f"Download failed: {download_result.get('error')}")
            result["download_error"] = download_result.get("error")
    
    return result

@app.get("/status")
async def status():
    """
    Get the current status of the automation
    """
    automation = app.state.automation
    if not automation:
        return {"status": "not_initialized"}
    
    return {
        "status": "ready",
        "logged_in": automation.logged_in
    }
