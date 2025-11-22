import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import IssueCategory, SolutionGuide, ServiceRequest

app = FastAPI(title="Mobile Repair Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _serialize(doc: dict) -> dict:
    """Convert Mongo types (ObjectId, datetime) to JSON-friendly values"""
    out = {}
    for k, v in doc.items():
        if k == "_id":
            out["id"] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        else:
            if isinstance(v, list):
                out[k] = [str(x) if hasattr(x, "__class__") and x.__class__.__name__ == "ObjectId" else x for x in v]
            else:
                out[k] = v
    return out


@app.get("/")
def read_root():
    return {"message": "Mobile Repair Assistant Backend Running"}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -------------------- API: Categories --------------------
@app.get("/api/categories")
def list_categories() -> List[dict]:
    docs = get_documents("issuecategory")
    return [_serialize(d) for d in docs]


# -------------------- API: Guides --------------------
@app.get("/api/guides")
def list_guides(category_key: Optional[str] = None) -> List[dict]:
    filt = {"category_key": category_key} if category_key else {}
    docs = get_documents("solutionguide", filt)
    return [_serialize(d) for d in docs]


# -------------------- API: Service Requests --------------------
class ServiceRequestResponse(BaseModel):
    id: str
    message: str


@app.post("/api/requests", response_model=ServiceRequestResponse)
def create_service_request(payload: ServiceRequest):
    try:
        new_id = create_document("servicerequest", payload)
        return {"id": new_id, "message": "Request submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- Seed sample data --------------------
@app.post("/api/seed")
def seed_sample_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    # Only seed if empty
    if db["issuecategory"].count_documents({}) == 0:
        categories: List[IssueCategory] = [
            IssueCategory(key="icloud", title="iCloud/Activation Lock", description="Help with activation lock and iCloud lock issues", icon="cloud"),
            IssueCategory(key="frp", title="FRP (Factory Reset Protection)", description="Google account lock/FRP bypass help", icon="shield"),
            IssueCategory(key="screen-lock", title="Screen/Pin/Pattern Lock", description="Forgotten screen lock resolutions", icon="lock"),
            IssueCategory(key="bootloop", title="Bootloop/No Boot", description="Device stuck on boot logo or not starting", icon="refresh"),
        ]
        for cat in categories:
            create_document("issuecategory", cat)

    if db["solutionguide"].count_documents({}) == 0:
        guides: List[SolutionGuide] = [
            SolutionGuide(
                title="Check Activation Lock Status",
                category_key="icloud",
                devices=["iPhone 8+", "iPad (2018+)"],
                summary="Verify activation lock status and prepare ownership proof",
                steps=[
                    {"title": "Find IMEI/Serial", "details": "From the SIM tray or box. If device is on, go to Settings > General > About."},
                    {"title": "Check Online", "details": "Use Apple's support to check coverage and activation lock status."},
                    {"title": "Contact Original Owner", "details": "Request remote removal via iCloud.com > Find My."}
                ],
                difficulty="medium",
            ),
            SolutionGuide(
                title="FRP Removal Preparation",
                category_key="frp",
                devices=["Samsung Galaxy S9+", "Pixel 3+"],
                summary="Collect details and follow safe FRP bypass preparation steps",
                steps=[
                    {"title": "Know the Patch Level", "details": "Find the Android security patch level to choose a compatible method."},
                    {"title": "Network Ready", "details": "Ensure stable Wi‑Fi; some steps require SIM with PIN."},
                    {"title": "OTG/PC Tools", "details": "Have a USB cable and a computer ready for ADB-based methods."}
                ],
                difficulty="hard",
            ),
            SolutionGuide(
                title="Forgot Screen PIN on Android",
                category_key="screen-lock",
                devices=["Android 8+"],
                summary="Try non-destructive options before reset",
                steps=[
                    {"title": "Find My Device Unlock", "details": "If enabled, use google.com/android/find to attempt unlock or reset."},
                    {"title": "OEM Account Unlock", "details": "Some vendors allow remote unlock after verification."},
                    {"title": "Backup then Reset", "details": "If nothing works, use recovery mode to factory reset (will erase data)."}
                ],
                difficulty="easy",
            ),
        ]
        for g in guides:
            create_document("solutionguide", g)

    return {"message": "Seed complete"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
