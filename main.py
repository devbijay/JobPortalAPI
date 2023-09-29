from dotenv import load_dotenv


import os
from typing import Union, List
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
def fetch_candidates(page: int = Query(default=1, description="Page number (default is 1)"),
                     city: str = Query(None, description="Filter by city"),
                     skills: str = Query(None, description="Filter by tech skills"),
                     db: Session = Depends(get_db)):
    limit = 10
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be greater than or equal to 1")

    skip = (page - 1) * limit

    query = db.query(models.CandidateDB)
    if city:
        query = query.filter(models.CandidateDB.city == city)

    if skills:
        query = query.filter(models.CandidateDB.skills.contains(skills))

    return query.offset(skip).limit(limit).all()


@app.get("/fetch-resume", )
def fetch_resume(candidate_id: int = Query(..., description="Candidate ID"),
                 db: Session = Depends(get_db)):
    candidate = db.query(models.CandidateDB).filter(models.CandidateDB.id == candidate_id).first()
    expiration_time = 3600
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.getenv("S3_BUCKET_NAME"), 'Key': f"{candidate.name}-{candidate.id}.pdf"},
        ExpiresIn=expiration_time
    )


@app.post("/add-candidates")
def fetch_candidates(candidates: List[schemas.CandidateCreate], db: Session = Depends(get_db)):
    db_candidates = [models.CandidateDB(**candidate.dict()) for candidate in candidates]
    print(db_candidates)
    try:
        with db.begin_nested():
            db.bulk_save_objects(db_candidates)
            db.commit()
            send_sqs(candidates)
            db.refresh(db_candidates)
    except Exception as e:
        db.rollback()
        print(e)
        return {"Status": "Error", "Message": "An error occurred while adding candidates"}

    return {"Status": "Success", "Message": "Candidates added successfully"}
