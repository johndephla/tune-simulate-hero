
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

app = FastAPI()

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenerateRequest(BaseModel):
    prompt: str
    style: str = None
    title: str = None
    instrumental: bool = True
    download: bool = True

@app.get("/status")
async def get_status():
    """Check if the server is running and the bot is logged in"""
    if not hasattr(app.state, "automation"):
        return {"status": "running", "logged_in": False, "connected": False, "error": "Automation not initialized"}
    
    # Get detailed status from automation
    automation_status = app.state.automation.get_status()
    
    return {
        "status": "running", 
        "logged_in": automation_status["logged_in"],
        "connected": automation_status["connected"],
        "error": automation_status["error"]
    }

@app.post("/generate")
async def generate_song(request: GenerateRequest):
    """Generate a song with the provided prompt"""
    if not hasattr(app.state, "automation"):
        raise HTTPException(status_code=500, detail="Automation not initialized")
    
    try:
        # Generate the song
        result = app.state.automation.generate_song(
            prompt=request.prompt,
            style=request.style,
            title=request.title,
            instrumental=request.instrumental
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate song"))
        
        # Download if requested
        if request.download:
            download_result = app.state.automation.download_song(result["url"])
            if download_result["success"]:
                result["file_path"] = download_result["file_path"]
            else:
                result["download_error"] = download_result.get("error", "Unknown download error")
        
        return result
    except Exception as e:
        logger.error(f"Error generating song: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}
