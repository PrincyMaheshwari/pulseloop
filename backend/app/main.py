from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import feed, content, quiz, admin, auth, user

app = FastAPI(
    title="PulseLoop API",
    description="B2B SaaS platform for industry trend awareness and learning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(feed.router, prefix="/api/feed", tags=["feed"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(user.router, prefix="/api/me", tags=["user"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "PulseLoop API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


