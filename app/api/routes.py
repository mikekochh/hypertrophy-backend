from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from app.db.models import Exercise, WorkoutPlan, WorkoutSession, WorkoutPlanExercises, CompletedWorkouts, CompletedExercises

router = APIRouter()

# --- GET Routes ---

@router.get("/")
async def root():
    return {"message": "Hello from FastAPI backend!"}

@router.get("/exercises")
async def get_exercises():
    exercises = await Exercise.find_all().to_list()
    return [{"id": str(ex.id), "exercise_name": ex.exercise_name} for ex in exercises]

# --- POST Payload Schemas ---

class ExerciseInput(BaseModel):
    exercise_id: str
    sets: int = Field(..., gt=0)

class SessionInput(BaseModel):
    name: str
    exercises: List[ExerciseInput]

class WorkoutPlanInput(BaseModel):
    name: str
    sessions: List[SessionInput]

# --- POST Route ---

@router.post("/create-workout-plan")
async def create_workout_plan(payload: WorkoutPlanInput):
    # Create the workout plan
    plan = WorkoutPlan(name=payload.name)
    await plan.insert()

    for session_data in payload.sessions:
        # Create the workout session
        session = WorkoutSession(name=session_data.name)
        await session.insert()

        # Create WorkoutPlanExercises for each exercise in this session
        for exercise_entry in session_data.exercises:
            plan_exercise = WorkoutPlanExercises(
                workout_session_id=session.id,
                exercise_id=ObjectId(exercise_entry.exercise_id),
                sets=exercise_entry.sets
            )
            await plan_exercise.insert()

    return {"message": "Workout plan created successfully!"}



@router.get("/workout-plans")
async def get_workout_plans():
    plans = await WorkoutPlan.find_all().to_list()
    return plans


@router.get("/workout-sessions")
async def get_workout_sessions():
    sessions = await WorkoutSession.find_all().to_list()
    return [{"id": str(s.id), "name": s.name} for s in sessions]


@router.get("/workout-sessions/{session_id}/exercises")
async def get_exercises_for_session(session_id: str):
    from app.db.models import WorkoutPlanExercises, Exercise
    from bson import ObjectId

    # Get all plan-exercise links for this session
    plan_exercises = await WorkoutPlanExercises.find(
        WorkoutPlanExercises.workout_session_id == ObjectId(session_id)
    ).to_list()

    # Fetch full exercise info
    result = []
    for pe in plan_exercises:
        exercise = await Exercise.get(pe.exercise_id)
        if exercise:
            result.append({
                "id": str(exercise.id),
                "exercise_name": exercise.exercise_name,
                "sets": pe.sets
            })

    return result


class CompletedSet(BaseModel):
    weight: int
    reps: int
    superset_weight: Optional[int] = None
    superset_reps: Optional[int] = None
    notes: Optional[str] = None

class CompletedExerciseInput(BaseModel):
    exercise_id: str
    sets: List[CompletedSet]

class CompletedWorkoutInput(BaseModel):
    workout_session_id: str
    workout_length: int
    workout_date: int
    exercises: List[CompletedExerciseInput]


@router.post("/log-workout")
async def log_completed_workout(payload: CompletedWorkoutInput):
    # Create the CompletedWorkout document
    workout = CompletedWorkouts(
        workout_session_id=ObjectId(payload.workout_session_id),
        workout_length=payload.workout_length,
        workout_date=payload.workout_date,
    )
    await workout.insert()

    # Save each exercise (flattened from sets)
    for exercise in payload.exercises:
        for set_data in exercise.sets:
            if not set_data.reps or set_data.reps == 0:
                continue  # ⛔ Skip sets with 0 reps

            total = (set_data.weight * set_data.reps) + (
                (set_data.superset_weight or 0) * (set_data.superset_reps or 0)
            )

            completed_exercise = CompletedExercises(
                completed_workout_id=workout.id,
                exercise_id=ObjectId(exercise.exercise_id),
                weight=set_data.weight,
                reps=set_data.reps,
                superset_weight=set_data.superset_weight,
                superset_reps=set_data.superset_reps,
                total_weight=total,
            )

            await completed_exercise.insert()

    return {"message": "Workout logged successfully"}

@router.get("/completed-workouts")
async def get_completed_workouts():
    workouts = await CompletedWorkouts.find_all().sort("-workout_date").to_list()

    print("workouts: ", workouts)

    result = []
    for w in workouts:
        session = await WorkoutSession.get(w.workout_session_id)
        result.append({
            "id": str(w.id),
            "workout_date": w.workout_date,
            "workout_length": w.workout_length,
            "session_name": session.name if session else "Unknown",
        })

    return result

from app.db.models import CompletedWorkouts, CompletedExercises, WorkoutSession, Exercise
from bson import ObjectId
from fastapi import HTTPException

@router.get("/completed-workouts/{workout_id}")
async def get_completed_workout(workout_id: str):
    workout = await CompletedWorkouts.get(ObjectId(workout_id))
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    session = await WorkoutSession.get(workout.workout_session_id)

    exercises = await CompletedExercises.find(
        CompletedExercises.completed_workout_id == workout.id
    ).to_list()

    enriched_exercises = []
    for e in exercises:
        exercise_doc = await Exercise.get(e.exercise_id)
        exercise_name = exercise_doc.exercise_name if exercise_doc else "Unknown"

        enriched_exercises.append({
            "exercise_id": str(e.exercise_id),
            "exercise_name": exercise_name,
            "weight": e.weight,
            "reps": e.reps,
            "superset_weight": e.superset_weight,
            "superset_reps": e.superset_reps,
            "total_weight": e.total_weight,
        })

    return {
        "id": str(workout.id),
        "workout_length": workout.workout_length,
        "workout_date": workout.workout_date,
        "session_name": session.name if session else "Unknown",
        "exercises": enriched_exercises,
    }



@router.delete("/reset-completed-workouts", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_completed_workouts():
    await CompletedWorkouts.find_all().delete()
    await CompletedExercises.find_all().delete()
    return
