from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import networkx as nx

# Database setup
DATABASE_URL = "postgresql://user:password@localhost/smart_waste"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI app
app = FastAPI()

# Database models
class Bin(Base):
    __tablename__ = "bins"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    level = Column(Float, default=0.0)

Base.metadata.create_all(bind=engine)

# Input models
class BinCreate(BaseModel):
    latitude: float
    longitude: float
    level: float = 0.0

class Route(BaseModel):
    source: int
    bins: list[int]

# Routes
@app.post("/add-bin/")
def add_bin(bin: BinCreate):
    db = SessionLocal()
    new_bin = Bin(latitude=bin.latitude, longitude=bin.longitude, level=bin.level)
    db.add(new_bin)
    db.commit()
    db.refresh(new_bin)
    db.close()
    return new_bin

@app.get("/get-route/")
def get_route(source_id: int):
    db = SessionLocal()
    bins = db.query(Bin).filter(Bin.level > 50).all()  # Collect bins >50% full
    db.close()
    
    G = nx.Graph()
    for bin in bins:
        G.add_node(bin.id, pos=(bin.latitude, bin.longitude))
    
    # Add dummy edges for simplicity (use real map data in production)
    for i, b1 in enumerate(bins):
        for j, b2 in enumerate(bins):
            if i != j:
                G.add_edge(b1.id, b2.id, weight=1)
    
    # Compute the shortest path using A*
    route = nx.astar_path(G, source=source_id, target=bins[0].id)
    return {"route": route}
