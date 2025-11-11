# app/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from auth import TOKEN_BLACKLIST
from database import SessionLocal
import crud, schemas

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> schemas.UserOut:
    
    print("=" * 60)
    print(f"🔍 Token validation started")
    print(f"🔍 Token (first 30 chars): {token[:30]}...")
    print(f"🔍 SECRET_KEY exists: {bool(SECRET_KEY)}")
    
    # Check if token is blacklisted
    if token in TOKEN_BLACKLIST:
        print("❌ Token is blacklisted")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print("🔓 Decoding JWT...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ JWT decoded successfully")
        print(f"📦 Payload: {payload}")
        
        email: str = payload.get("sub")  # ← Changed from 'username' to 'email'
        print(f"📧 Email from token: {email}")
        
        if email is None:
            print("❌ No 'sub' field in token")
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        print(f"❌ JWT decode error: {type(e).__name__} - {str(e)}")
        raise credentials_exception
    
    # ✅ FIX: Search by email, not username!
    user = crud.get_user_by_email(db, email)  # ← Changed this line
    
    if user is None:
        print(f"❌ User with email '{email}' not found in database")
        raise credentials_exception
    
    print(f"✅ User authenticated: {user.username} ({user.email})")
    print("=" * 60)
    
    return user