from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import io
import csv
import os

# MongoDB connection - support both local Docker and MongoDB Atlas
MONGODB_URI = "mongodb+srv://lawderlin:U2yaS5KwwXkxsVwK@emogo-backend.wm1wlle.mongodb.net/"
DB_NAME = os.getenv("MONGODB_DB", "emogo_db")
COLLECTION_NAME = "mood_records"

print(f"Connecting to MongoDB at: {MONGODB_URI.split('@')[-1] if '@' in MONGODB_URI else MONGODB_URI}")

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("✓ MongoDB connection successful")
except ConnectionFailure as e:
    print(f"✗ MongoDB connection failed: {e}")
    print("Running in demo mode - data will not persist")
    db = None
    collection = None

# Data Models
class MoodRecord(BaseModel):
    """Mood record with location and activity data"""
    mood: int = Field(..., ge=1, le=5, description="Mood scale from 1 to 5")
    activity: Optional[str] = None
    longitude: float
    latitude: float
    video_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "mood": 4,
                "activity": "working",
                "longitude": 121.5654,
                "latitude": 25.0330,
                "video_url": "s3://bucket/video.mp4"
            }
        }

class MoodRecordResponse(MoodRecord):
    id: str = Field(..., alias="_id")

# FastAPI app
app = FastAPI(
    title="EmoGo Backend",
    description="Backend API for EmoGo mood tracking application",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {
        "message": "EmoGo Backend API",
        "version": "0.1.0",
        "status": "running",
        "db_status": "connected" if collection else "demo_mode"
    }

@app.post("/api/records", response_model=dict)
async def create_record(record: MoodRecord):
    """Create a new mood record"""
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    record_dict = record.model_dump()
    result = collection.insert_one(record_dict)
    
    return {
        "id": str(result.inserted_id),
        "message": "Record created successfully",
        "data": record_dict
    }

@app.get("/api/records")
async def get_records(limit: int = 100):
    """Get all mood records"""
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    records = list(collection.find().limit(limit))
    return {
        "count": len(records),
        "records": [
            {**record, "_id": str(record["_id"])} 
            for record in records
        ]
    }

@app.get("/api/records/{record_id}")
async def get_record(record_id: str):
    """Get a specific mood record"""
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    from bson import ObjectId
    try:
        record = collection.find_one({"_id": ObjectId(record_id)})
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        record["_id"] = str(record["_id"])
        return record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/export/csv")
async def export_csv():
    """Export all mood records as CSV"""
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    records = list(collection.find())
    if not records:
        raise HTTPException(status_code=404, detail="No records to export")
    
    # Create CSV
    output = io.StringIO()
    fieldnames = ["id", "mood", "activity", "longitude", "latitude", "video_url", "created_at"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for record in records:
        record["id"] = str(record["_id"])
        writer.writerow({field: record.get(field, "") for field in fieldnames})
    
    # Convert to bytes
    output.seek(0)
    return FileResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mood_records.csv"}
    )

@app.post("/api/records/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file (demo endpoint)"""
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    filename = file.filename
    return {
        "message": "Video uploaded successfully",
        "filename": filename,
        "content_type": file.content_type,
        "note": "In production, save to S3 or cloud storage"
    }

@app.get("/api/stats")
async def get_stats():
    """Get mood statistics"""
    if collection is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    records = list(collection.find())
    if not records:
        return {"message": "No records available"}
    
    moods = [r.get("mood", 0) for r in records if "mood" in r]
    
    return {
        "total_records": len(records),
        "average_mood": sum(moods) / len(moods) if moods else 0,
        "mood_distribution": {
            i: sum(1 for m in moods if m == i)
            for i in range(1, 6)
        }
    }