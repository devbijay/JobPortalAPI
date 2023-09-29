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
    pass




class CandidateUpdate(CandidateBase):
    pass


class Candidate(CandidateBase):
    class Config:
        orm_mode = True
