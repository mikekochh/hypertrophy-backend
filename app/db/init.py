from beanie import init_beanie
import motor.motor_asyncio
from app.db.models import Exercise, WorkoutPlan, WorkoutSession, WorkoutPlanExercises, CompletedExercises, CompletedWorkouts
from os import getenv
from dotenv import load_dotenv

load_dotenv()

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(getenv("MONGODB_URI"))
    db = client[getenv("MONGODB_DB_NAME")]
    
    await init_beanie(
        database=db,
        document_models=[
            Exercise,
            WorkoutPlan,
            WorkoutSession,
            WorkoutPlanExercises,
            CompletedWorkouts,
            CompletedExercises
        ]
    )
