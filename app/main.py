from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from app.config import settings  

#  environment variables
load_dotenv()

# FastAPI app 
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="NourishSA Backend API - Fighting food waste in South Africa",
    debug=settings.DEBUG
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    try:
        
        response = supabase.table("user_profiles").select("count").execute()
        return {
            "status": "healthy",
            "database": "connected",
            "app": settings.APP_NAME
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


@app.get("/test-tables")
async def test_tables():
    tables = ["user_profiles", "food_items", "meals", "nutrition_goals"]
    results = {}
    
    for table in tables:
        try:
            response = supabase.table(table).select("*", count="exact").execute()
            results[table] = {
                "exists": True,
                "count": response.count if response.count is not None else 0
            }
        except Exception as e:
            results[table] = {
                "exists": False,
                "error": str(e)
            }
    
    return {"tables": results}

@app.get("/api/food-items")
async def get_food_items(limit: int = 10):
    try:
        result = supabase.table('food_items').select("*").limit(limit).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/food-items/{food_id}")
async def get_food_item(food_id: str):
    try:
        result = supabase.table('food_items').select("*").eq('id', food_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Food item not found")
        return {"success": True, "data": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)