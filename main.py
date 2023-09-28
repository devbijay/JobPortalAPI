from typing import Union, List

from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, get_db, engine

from fastapi import FastAPI, Query, Depends, HTTPException

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Candidates API")


@app.get("/fetch-candidates", response_model=List[schemas.Candidate])
def fetch_candidates(page: int = Query(default=1, description="Page number (default is 1)"),
                     db: Session = Depends(get_db)):
    limit = 10
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be greater than or equal to 1")

    skip = (page - 1) * limit
    return db.query(models.CandidateDB).offset(skip).limit(limit).all()


@app.post("/add-candidates")
def fetch_candidates(candidates: List[schemas.CandidateCreate], db: Session = Depends(get_db)):
    db_candidates = [models.CandidateDB(**candidate.dict()) for candidate in candidates]
    print(db_candidates)
    try:
        with db.begin_nested():
            db.bulk_save_objects(db_candidates)
            db.commit()
            db.refresh(db_candidates)
    except Exception as e:
        db.rollback()
        print(e)
        return {"Status": "Error", "Message": "An error occurred while adding candidates"}

    return {"Status": "Success", "Message": "Candidates added successfully"}
