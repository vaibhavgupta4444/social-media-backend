from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database.connection import engine, Base
from app.routers import users, posts, likes, comments, follow, notifications, subscription, vapid
from app.core.socketio_manager import sio
import socketio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)

# Configure CORS - MUST be first middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(follow.router)
app.include_router(notifications.router)
app.include_router(subscription.router)
app.include_router(vapid.router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "FastAPI project running"}

@app.get("/socket/status", tags=["Socket"])
def socket_status():
    from app.core.socketio_manager import get_connected_users_count
    return {
        "status": "active",
        "connected_users": get_connected_users_count()
    }

# IMPORTANT: Create Socket.IO ASGI application - this must be AFTER all routes are defined
socket_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path='socket.io'
)