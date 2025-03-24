from beanie import Document
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class Exercise(Document):
    exercise_name: str = Field(..., description="Name of the exercise")

    class Settings:
        name = "exercises"


class WorkoutPlan(Document):
    name: str = Field(..., description="Name of the workout plan")

    class Settings:
        name = "workout_plans"

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WorkoutSession(Document):
    name: str = Field(..., description="Name of workout session")
    workout_plan_id: ObjectId = Field(...)

    class Settings:
        name = "workout_sessions"

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WorkoutPlanExercises(Document):
    workout_session_id: ObjectId = Field(...)
    exercise_id: ObjectId = Field(...)
    sets: int = Field(..., gt=0)

    class Settings:
        name = "workout_plan_exercises"

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CompletedWorkouts(Document):
    workout_length: int = Field(..., description="Workout duration in seconds")
    workout_date: int = Field(..., description="Timestamp or date ID (e.g. Unix timestamp)")
    workout_session_id: ObjectId = Field(...)

    class Settings:
        name = "completed_workouts"

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CompletedExercises(Document):
    completed_workout_id: ObjectId = Field(...)
    exercise_id: ObjectId = Field(...)
    weight: int = Field(...)
    reps: int = Field(...)
    superset_weight: Optional[int] = Field(default=None)
    superset_reps: Optional[int] = Field(default=None)
    total_weight: int = Field(...)

    class Settings:
        name = "completed_exercises"

    model_config = ConfigDict(arbitrary_types_allowed=True)

