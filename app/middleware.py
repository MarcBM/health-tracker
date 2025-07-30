from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from app.database import SessionLocal, User

load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect routes and redirect unauthenticated users to login
    """
    
    # Routes that don't require authentication
    PUBLIC_ROUTES = {
        "/login",
        "/health",
        "/static"  # For static files (CSS, JS, images)
    }
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Check authentication for all routes except public ones
        """
        path = request.url.path
        
        # Allow public routes
        if self.is_public_route(path):
            return await call_next(request)
        
        # Check for authentication and extract user
        user = self.get_authenticated_user(request)
        if not user:
            # Redirect to login page for web requests
            if self.is_web_request(request):
                return RedirectResponse(url="/login", status_code=302)
            else:
                # Return 401 for API requests
                return Response(
                    content='{"detail": "Not authenticated"}',
                    status_code=401,
                    media_type="application/json"
                )
        
        # Attach user to request state
        request.state.user = user
        
        # User is authenticated, proceed with request
        return await call_next(request)
    
    def is_public_route(self, path: str) -> bool:
        """Check if the route is public (doesn't require authentication)"""
        # Exact matches
        if path in self.PUBLIC_ROUTES:
            return True
        
        # Static files (starts with /static/)
        if path.startswith("/static/"):
            return True
            
        return False
    
    def get_authenticated_user(self, request: Request) -> User:
        """Extract and validate user from JWT token, return User object or None"""
        # Check for token in cookie first
        token = request.cookies.get("access_token")
        
        if token:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]
        else:
            # Check Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
            else:
                return None
        
        # Validate token and get user
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if not username:
                return None
            
            # Get user from database
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.username == username).first()
                return user
            finally:
                db.close()
                
        except JWTError:
            return None
    
    def is_web_request(self, request: Request) -> bool:
        """Determine if this is a web browser request vs API request"""
        accept_header = request.headers.get("accept", "")
        # If the request accepts HTML, it's likely a browser request
        return "text/html" in accept_header 