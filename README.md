# Social Media Backend API

A comprehensive FastAPI-based social media backend with user authentication, posts, comments, likes, follow system, and real-time notifications.

## Features

### 🔐 Authentication & User Management
- User registration with email verification (OTP)
- Login with JWT access and refresh tokens
- Password change and reset functionality
- Secure password hashing with bcrypt
- Email verification required for all actions

### 📝 Posts
- Create posts with text and/or media
- Upload media files to Cloudinary
- Public and private post visibility
- Pagination support
- Update and delete own posts
- Author username displayed

### ❤️ Likes
- Like/unlike posts
- Automatic like count tracking
- Prevent duplicate likes
- Notifications on new likes

### 💬 Comments
- Comment on posts
- Update and delete own comments
- Pagination for comments
- Display commenter username
- Notifications on new comments

### 👥 Follow System
- Follow/unfollow users
- Get followers and following lists
- Prevent self-following
- Notifications on new followers

### 🔔 Notifications
- **Real-time notifications via Socket.IO** for:
  - New followers
  - Post likes
  - Post comments
- Mark notifications as read (single or all)
- Delete notifications
- Pagination and unread filter
- WebSocket connections with JWT authentication
- Live notification delivery to connected users

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Email**: SMTP
- **Media Storage**: Cloudinary
- **Validation**: Pydantic
- **Real-time**: Socket.IO (python-socketio)

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- Cloudinary account (for media uploads)
- SMTP email account (Gmail recommended)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd social-media-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
- Database credentials
- JWT secret key (generate a strong random key)
- SMTP email settings
- Cloudinary credentials

5. **Initialize database**
```bash
# Create database migrations
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

6. **Run the application**
```bash
# IMPORTANT: Use socket_app instead of app to enable Socket.IO
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
Socket.IO will be available at `ws://localhost:8000/socket.io/`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication & Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/register` | Register new user | No |
| POST | `/users/verify-otp` | Verify email with OTP | No |
| POST | `/users/login` | Login user | No |
| GET | `/users/refresh` | Refresh access token | Yes |
| POST | `/users/change-password` | Change password | Yes (Verified) |
| POST | `/users/forgot-password` | Request password reset | No |
| POST | `/users/reset-password` | Reset password with token | No |

### Posts

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/posts/` | Create new post | Yes (Verified) |
| GET | `/posts/` | Get all posts (paginated) | Yes (Verified) |
| GET | `/posts/{post_id}` | Get single post | Yes (Verified) |
| PUT | `/posts/{post_id}` | Update post | Yes (Verified) |
| DELETE | `/posts/{post_id}` | Delete post | Yes (Verified) |

### Likes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/posts/{post_id}/like` | Like a post | Yes (Verified) |
| DELETE | `/posts/{post_id}/like` | Unlike a post | Yes (Verified) |

### Comments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/posts/{post_id}/comment` | Create comment | Yes (Verified) |
| GET | `/posts/{post_id}/comment` | Get comments (paginated) | No |
| PUT | `/posts/{post_id}/comment/{id}` | Update comment | Yes (Verified) |
| DELETE | `/posts/{post_id}/comment/{id}` | Delete comment | Yes (Verified) |

### Follow System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/users/{user_id}/follow` | Follow user | Yes (Verified) |
| DELETE | `/users/{user_id}/unfollow` | Unfollow user | Yes (Verified) |
| GET | `/users/{user_id}/followers` | Get followers list | No |
| GET | `/users/{user_id}/following` | Get following list | No |

### Notifications

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/notifications/` | Get notifications (paginated) | Yes (Verified) |
| PUT | `/notifications/{notification_id}/read` | Mark as read | Yes (Verified) |
| PUT | `/notifications/read-all` | Mark all as read | Yes (Verified) |
| DELETE | `/notifications/{notification_id}` | Delete notification | Yes (Verified) |

## Environment Variables

See `.env.example` for all required environment variables.

### Key Configuration:

**Database**
- `DATABASE_URL`: PostgreSQL connection string

**JWT**
- `SECRET_KEY`: Secret key for JWT encoding (generate a strong random key)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)

**Email (SMTP)**
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port (587 for TLS)
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password (use app-specific password for Gmail)

**Cloudinary**
- `CLOUDINARY_CLOUD_NAME`: Your Cloudinary cloud name
- `CLOUDINARY_API_KEY`: Your Cloudinary API key
- `CLOUDINARY_API_SECRET`: Your Cloudinary API secret

## Project Structure

```
social-media-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   ├── security.py         # Authentication & password utilities
│   │   ├── email.py            # Email sending functions
│   │   └── cloudinary_upload.py # Media upload utilities
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py       # Database connection setup
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py             # Authentication dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── users.py            # User model
│   │   ├── posts.py            # Post, Comment, Like models
│   │   ├── follow.py           # Follow model
│   │   └── notifications.py    # Notification model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── users.py            # User schemas
│   │   ├── posts.py            # Post schemas
│   │   ├── comments.py         # Comment schemas
│   │   ├── follow.py           # Follow schemas
│   │   └── notifications.py    # Notification schemas
│   └── routers/
│       ├── __init__.py
│       ├── users.py            # User routes
│       ├── posts.py            # Post routes
│       ├── likes.py            # Like routes
│       ├── comments.py         # Comment routes
│       ├── follow.py           # Follow routes
│       └── notifications.py    # Notification routes
├── alembic/                    # Database migrations
├── .env                        # Environment variables (not in git)
├── .env.example               # Example environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Database Models

### User
- id, username, email, hashed_password
- is_active, is_verified
- OTP fields for email verification
- Relationships: posts, comments, likes, followers, following, notifications

### Post
- id, user_id, content, media_url
- is_private, likes_count
- created_at, updated_at
- Relationships: author, comments, likes

### Comment
- id, post_id, user_id, content
- created_at, updated_at
- Relationships: post, author

### Like
- id, post_id, user_id
- created_at
- Relationships: post, user

### Follow
- id, follower_id, following_id
- created_at
- Relationships: follower_user, following_user

### Notification
- id, user_id, actor_id, type
- post_id, comment_id (optional)
- is_read, created_at
- Relationships: user, actor, post, comment

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Email verification required for account activation
- Access and refresh token system
- Secure password reset with time-limited tokens
- User verification checks on all protected routes
- Authorization checks (users can only modify their own content)
- SQL injection protection via SQLAlchemy ORM

## Real-Time Notifications with Socket.IO

This backend includes Socket.IO integration for real-time notifications. Users receive instant updates when:
- Someone follows them
- Someone likes their post
- Someone comments on their post

### Quick Start

#### Server
The Socket.IO server is automatically started when running the application with `socket_app`:
```bash
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8000
```

#### Client Connection (JavaScript/React)
```javascript
import io from 'socket.io-client';

const token = localStorage.getItem('access_token');
const socket = io('http://localhost:8000', {
  path: '/socket.io/',
  query: { token },
  transports: ['websocket', 'polling']
});

socket.on('connected', (data) => {
  console.log('Connected:', data.message);
});

socket.on('new_notification', (notification) => {
  console.log('New notification:', notification);
  // Update UI with notification
});
```

#### Check Connection Status
```bash
curl http://localhost:8000/socket/status
```

### Notification Format
```json
{
  "id": 123,
  "type": "like",
  "actor_username": "john_doe",
  "actor_id": 45,
  "post_id": 789,
  "is_read": false,
  "created_at": "2026-01-23T10:30:00",
  "message": "john_doe liked your post"
}
```

### Features
- ✅ JWT-based authentication for WebSocket connections
- ✅ Automatic reconnection handling
- ✅ User session management
- ✅ Real-time notification delivery
- ✅ Fallback to database polling for offline users
- ✅ CORS support for web clients

### Documentation
For detailed Socket.IO implementation, client examples, and troubleshooting, see [SOCKETIO_DOCUMENTATION.md](SOCKETIO_DOCUMENTATION.md)

## Development

### Running Tests
```bash
pytest
```

### Creating Database Migrations
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write descriptive docstrings

## Deployment

### Production Checklist
1. Set `DEBUG=False` in production
2. Use strong `SECRET_KEY`
3. Configure proper CORS settings
4. Use environment variables for sensitive data
5. Set up SSL/TLS certificates
6. Configure PostgreSQL for production
7. Set up proper logging
8. Use process manager (e.g., gunicorn, supervisor)
9. Configure reverse proxy (e.g., nginx)
10. Set up monitoring and error tracking

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
