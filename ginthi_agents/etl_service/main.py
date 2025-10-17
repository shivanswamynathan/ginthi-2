from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from etl_service.api.routes import reports

app = FastAPI(title="SupplyNote GRN Report ETL Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports.router)

@app.get("/")
def root():
    return {"message": "SupplyNote GRN Report Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)