"""
Social Media Automation API
Multi-user platform for automated social media posting
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uvicorn
import os

from .database import engine, get_db, create_tables
from .models import User, SocialMediaCredential, Post, PostPlatform
from .auth import authenticate_user, create_access_token, get_current_user
from .routers import auth, credentials, posts, platforms
from .config import settings

# Import scheduler
from scheduler import start_scheduler, stop_scheduler

# Create database tables
create_tables()

app = FastAPI(
    title="Social Media Automation API",
    description="Multi-user platform for automated social media posting with AI content generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (project root for index.html and other static files)
static_dir = os.path.dirname(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve the main web UI at root
@app.get("/")
async def serve_index():
    """Serve the main web interface"""
    # index.html is in the parent directory (project root)
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    return HTMLResponse(content="<h1>Social Media Automation Platform</h1><p>Web UI not found. Check server setup.</p>", status_code=200)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Start background scheduler on app startup"""
    print("STARTING HIVE APPLICATION...", flush=True)
    start_scheduler()
    print("Background scheduler started", flush=True)
    print("Hive server ready at http://localhost:8000", flush=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler on app shutdown"""
    print("Shutting down Hive application...", flush=True)
    stop_scheduler()
    print("Application shutdown complete", flush=True)

# Configure logging to be visible
import logging
import sys

# Force logging to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    stream=sys.stdout,
    force=True
)

print("=== HIVE APPLICATION STARTING ===", flush=True)
print("FastAPI app initialized", flush=True)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
print("Auth router loaded", flush=True)

app.include_router(credentials.router, prefix="/api/credentials", tags=["Credentials"])
print("Credentials router loaded", flush=True)

app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
print("Posts router loaded", flush=True)

app.include_router(platforms.router, prefix="/api/platforms", tags=["Platforms"])
print("Platforms router loaded", flush=True)

@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Social Media Automation API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "web_ui": "/"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/debug-token")
async def debug_token(token: str):
    """Debug endpoint to decode and validate JWT tokens"""
    try:
        from jose import jwt, JWTError
        from .config import settings

        print(f"DEBUG ENDPOINT: Decoding token: {token[:20]}...")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print(f"DEBUG ENDPOINT: Token payload: {payload}")

        from .database import get_db
        from sqlalchemy.orm import Session
        from .models import User

        db = next(get_db())
        email = payload.get("sub")
        if email:
            user = db.query(User).filter(User.email == email).first()
            if user:
                print(f"DEBUG ENDPOINT: User found: {user.email}")
                return {
                    "valid": True,
                    "payload": payload,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name
                    }
                }
            else:
                print(f"DEBUG ENDPOINT: User not found for email: {email}")
                return {"valid": False, "error": f"User not found: {email}"}
        else:
            return {"valid": False, "error": "No 'sub' field in token"}

    except JWTError as e:
        print(f"DEBUG ENDPOINT: JWT Error: {e}")
        return {"valid": False, "error": f"JWT Error: {str(e)}"}
    except Exception as e:
        print(f"DEBUG ENDPOINT: Unexpected error: {e}")
        return {"valid": False, "error": f"Unexpected error: {str(e)}"}

@app.get("/api/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )