from typing import Optional

from pydantic import BaseModel


class CandidateBase(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    city: str
    full_address: str
    skills: str


class CandidateCreate(CandidateBase):
    id: Optional[int] = None




class CandidateUpdate(CandidateBase):
    pass


class Candidate(CandidateBase):
    class Config:
        orm_mode = True


class ResumeLink(BaseModel):
    link: str