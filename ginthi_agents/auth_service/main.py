from fastapi import FastAPI
from auth_service.db.database import engine, Base


from auth_service.schemas.central_db import (
    Clients, LeadAdmins, ClientAPIKeys, ClientServers,
    Workflows, WorkflowExecutions,
    AICreditLedger, AICreditEntries,
    Feedback
)

auth_service = FastAPI(title="Central DB API")

@auth_service.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

@auth_service.get("/")
def root():
    return {"message": "Central DB API is running"}