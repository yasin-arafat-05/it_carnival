from fastapi import Depends
from app.core.config import CONFIG
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

connection_string = CONFIG.DATABASE_URL
print(f"{connection_string}")

#============Why connection_args??=================
#1st connection establishement takes times
#Sometimes can be occur TimeError:
#To solve keep the connection alive 
connection_args = {
    "server_settings": {
        "jit": "off", 
        "tcp_keepalives_idle": "60", 
        "tcp_keepalives_interval": "10",
        "tcp_keepalives_count": "3",
        "statement_timeout": "30000" 
    }
}

async_engine = create_async_engine(
    url=connection_string,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,
    pool_pre_ping=True,
    echo=False,
    connect_args=connection_args,
    # Additional performance settings
    # Set to True for debugging pool issues
    echo_pool=False, 
    # Hide parameters in logs for security
    hide_parameters=True  
)


asyncSession = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()