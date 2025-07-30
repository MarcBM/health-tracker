from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

# Import database components
from app.database import get_db, User

router = APIRouter(tags=["authentication"])

# Templates setup
templates = Jinja2Templates(directory="app/templates")

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Security scheme
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    id: int
    username: str
    can_edit: bool

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class PasswordChangeResponse(BaseModel):
    message: str

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate hash for a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user against database"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page for user authentication"""
    # Check if user is already logged in
    token = request.cookies.get("access_token")
    if token:
        from jose import jwt, JWTError
        import os
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]
            
            SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("sub"):
                # User is already logged in, redirect to dashboard
                return RedirectResponse(url="/", status_code=302)
        except JWTError:
            # Token is invalid, continue to login page
            pass
    
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handle both form-based and API login requests
    """
    # Authenticate user against database
    user = authenticate_user(db, username, password)
    if not user:
        # Check if this is a form request (has HTML accept header)
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header:
            # Redirect back to login with error for form requests
            return RedirectResponse(url="/login?error=invalid_credentials", status_code=status.HTTP_302_FOUND)
        else:
            # Return JSON error for API requests
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Create access token with user info
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "can_edit": user.can_edit
        },
        expires_delta=access_token_expires
    )
    
    # Check if this is a form request or API request
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        # Form request - set cookie and redirect
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        return response
    else:
        # API request - return JSON
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        can_edit=current_user.can_edit
    )

@router.get("/logout")
async def logout():
    """
    Logout user - clears auth cookie and redirects to login
    """
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    """
    Display the password change form - redirect to dashboard for now
    """
    from fastapi.responses import RedirectResponse
    # TODO: Create a password change page or integrate into settings
    return RedirectResponse(url="/", status_code=302)

@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password by providing old and new passwords
    """
    # Verify the old password
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Validate new password (add any password requirements here)
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    # Hash the new password
    new_hashed_password = get_password_hash(request.new_password)
    
    # Update the user's password in the database
    current_user.hashed_password = new_hashed_password
    db.commit()
    db.refresh(current_user)
    
    return PasswordChangeResponse(message="Password changed successfully") 