import json

import uvicorn
from dotenv import load_dotenv

import os
from typing import Union, List, Optional
from sqlalchemy.orm import Session

import models
import schemas
from aws_util import s3, send_sqs
from database import SessionLocal, get_db, engine

from fastapi import FastAPI, Query, Depends, HTTPException

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Candidates API")


@app.get("/fetch-candidates", response_model=List[schemas.Candidate])
def fetch_candidates(email: str = Query(None, description="Filter by candidate email"),
                     city: str = Query(None, description="Filter by city"),
                     skills: str = Query(None, description="Filter by tech skills"),
                     page: int = Query(default=1, description="Page number (default is 1)", ge=1),
                     limit: int = Query(10, description="Result Per Page", ge=1, le=10),
                     db: Session = Depends(get_db)):

    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be greater than or equal to 1")

    skip = (page - 1) * limit

    query = db.query(models.CandidateDB)

    if email:
        query = query.filter(models.CandidateDB.email == email)

    if city:
        query = query.filter(models.CandidateDB.city == city)

    if skills:
        query = query.filter(models.CandidateDB.skills.contains(skills))

    return query.offset(skip).limit(limit).all()


@app.get("/fetch-resume", response_model=schemas.ResumeLink)
def fetch_resume(candidate_id: Optional[int] = Query(None, description="Candidate ID"),
                 candidate_email: Optional[str] = Query(None, description="Candidate Email"),
                 db: Session = Depends(get_db)):
    if candidate_id is None and candidate_email is None:
        raise HTTPException(status_code=400, detail="Either candidate_id or candidate_email must be provided")

    candidate = None
    if candidate_id:
        candidate = db.query(models.CandidateDB).filter(models.CandidateDB.id == candidate_id).first()
    else:
        candidate = db.query(models.CandidateDB).filter(models.CandidateDB.email == candidate_email).first()

    if not candidate:
        raise HTTPException(status_code=400, detail="Either candidate_id or candidate_email is invalid")

    expiration_time = 3600
    link = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.getenv("S3_BUCKET_NAME"), 'Key': f"resume/{candidate.email}.pdf"},
        ExpiresIn=expiration_time
    )
    return schemas.ResumeLink(link=link)


@app.post("/add-candidates")
def fetch_candidates(candidates: List[schemas.CandidateCreate], db: Session = Depends(get_db)):
    db_candidates = [models.CandidateDB(**candidate.dict()) for candidate in candidates]
    print(db_candidates)
    with db.begin_nested():
        db.bulk_save_objects(db_candidates)
        db.commit()
        json_data = json.dumps([candidate.dict() for candidate in candidates])
        print(json_data)
        send_sqs(json_data)

    return {"Status": "Success", "Message": "Candidates added successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
