from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, movies, showtimes, reservations, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Reservation API",
    description="Backend for movie ticket reservation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(showtimes.router)
app.include_router(reservations.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Movie Reservation API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}