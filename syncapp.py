from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

engine = create_engine('sqlite:///db.sqlite3', connect_args={
    "check_same_thread": False
})
LocalSession = sessionmaker(engine)
Base = declarative_base()

# Define the tables models

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)

Base.metadata.create_all(engine)

def get_db() -> Session:
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

# Define the Pydentic schema

class UserSchema(BaseModel):
    username: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Lifespan method....')
    yield

app = FastAPI(title="Synchronouse API Test",
              debug=True,
              lifespan=lifespan)

@app.get('/users')
def get_users(db: Session = Depends(get_db)):
    res = db.query(User).all()
    return {"users": res}

@app.post('/users')
def add_user(user: UserSchema, db: Session = Depends(get_db)):
    add_user = User(username=user.username)
    try:
        db.add(add_user)
        db.commit()
        db.refresh(add_user)
    except Exception as ex:
        return {
            "errors": str(ex)
        }
    return add_user