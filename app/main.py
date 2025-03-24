from fastapi import FastAPI
from app.db.init import init_db
from app.api.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()  # 👈 This is what registers the models with Beanie

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://hypertrophy-frontend.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
