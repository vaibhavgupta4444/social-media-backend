import socketio
from typing import Optional
from app.models import User
from app.core.security import decode_access_token
from app.database.connection import SessionLocal
from urllib.parse import parse_qs

# Create Socket.IO server instance
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[
        "*"
    ],
    logger=True,
    engineio_logger=True
)

# Dictionary to store user_id to session_id mapping
connected_users = {}


async def authenticate_socket(environ):
    """Authenticate socket connection using JWT token from query params"""
    try:
        # Get token from query parameters
        query_string = environ.get('QUERY_STRING', '')
        print(f"Query string received: {query_string}")
        
        # Parse query string properly
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        print(f"Token extracted: {token[:20] if token else 'None'}...")
        
        if not token:
            print("No token provided")
            return None
        
        # Verify token using security module
        payload = decode_access_token(token)
        if not payload:
            print("Invalid token")
            return None
        
        print(f"Token payload: {payload}")
        user_id = payload.get("sub")
        print(f"User ID from token: {user_id}")
        return user_id
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    user_id = await authenticate_socket(environ)
    if user_id is None:
        print(f"Connection rejected for sid: {sid} - Authentication failed")
        return False  # Reject connection
    
    # Store the connection
    connected_users[str(user_id)] = sid
    print(f"User {user_id} connected with session {sid}")
    
    # Send connection success message
    await sio.emit('connected', {'message': 'Connected to notification service'}, room=sid)
    
    return True  # Accept connection


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    # Find and remove user from connected_users
    user_id_to_remove = None
    for user_id, session_id in connected_users.items():
        if session_id == sid:
            user_id_to_remove = user_id
            break
    
    if user_id_to_remove:
        del connected_users[user_id_to_remove]
        print(f"User {user_id_to_remove} disconnected")
    else:
        print(f"Unknown session {sid} disconnected")


async def send_notification_to_user(user_id: int, notification_data: dict):
    
    session_id = connected_users.get(str(user_id))
  
    if session_id:
        try:
            await sio.emit('new_notification', notification_data, room=session_id)
            print(f"Notification sent to user {user_id}")
            return True
        except Exception as e:
            print(f"Error sending notification to user {user_id}: {e}")
            return False
    else:
        print(f"User {user_id} is not connected")
        return False


def get_connected_users_count():
    """Get the number of currently connected users"""
    return len(connected_users)


def is_user_connected(user_id: int) -> bool:
    """Check if a user is currently connected"""
    return str(user_id) in connected_users
