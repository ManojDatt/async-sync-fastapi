from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy import Integer, Column, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pydantic import BaseModel

engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3', connect_args={
    "check_same_thread": False
})
LocalSession = async_sessionmaker(engine)

# Define the tables models

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)

async def get_db() -> AsyncSession:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    db = LocalSession()
    try:
        yield db
    finally:
        await db.close()

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
async def get_users(db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(User))
    res = results.scalars().all()
    return {"users": res}

@app.post('/users')
async def add_user(user: UserSchema, db: AsyncSession = Depends(get_db)):
    add_user = User(username=user.username)
    try:
        db.add(add_user)
        await db.commit()
        await db.refresh(add_user)
    except Exception as ex:
        return {
            "errors": str(ex)
        }
    return add_user