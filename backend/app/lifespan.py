from fastapi import FastAPI
from sqlalchemy.sql import text 
from psycopg.rows import dict_row
from app.database.base import Base
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from app.database.session import asyncSession, async_engine

#"""
# tables.BASE.metadata.create_all(bind=async_engine): synchronous:
# asynchronous: advance guide: Lifespan fastapi Documentation:
# yeild give the control to fastapi, it's working procedure 
# is different when work with a context manager.
#"""
@asynccontextmanager
async def lifespan(app:FastAPI):
    #--------------------Applicatoin startup------------------
    print("Application startup started")
    
    try:
        # a.Create Database Schema:
        async with async_engine.begin() as conn:
            print("Database connection established")
            # Postgres advisory lock দিয়ে একবারে একটা container-ই schema create করবে
            await conn.execute(text("SELECT pg_advisory_lock(123456789)"))
            try:
                await conn.run_sync(Base.metadata.create_all)
            finally:
                await conn.execute(text("SELECT pg_advisory_unlock(123456789)"))
            print("Application startup completed")
            
        #b.Compile the langgraph checkpointer and keep connection alive for app lifetime:
        # future implementation:

        # give the control to fastapi:
        yield
    except Exception as e:
        print(f"Startup error: {e}")
        raise

    
    #--------------------Applicatoin Shutdown------------------
    # when it will execute
    # crtl + c 
    # uvicoron stop 
    print("Application shutdown started")
    try:
        # Pool/connection are closed by the context manager above
        await async_engine.dispose()
        print("Database connections closed")
    except Exception as e:
        print(f"Shutdown error: {e}")
    print("Application shutdown completed")