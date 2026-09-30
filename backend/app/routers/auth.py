import os

from datetime import datetime, timedelta, timezone

import bcrypt

from dotenv import load_dotenv

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from jose import (
    JWTError,
    jwt
)

from pydantic import (
    BaseModel,
    EmailStr
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import User


load_dotenv()


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


SECRET_KEY = os.getenv(
    "SECRET_KEY"
)


if not SECRET_KEY:

    raise RuntimeError(
        "SECRET_KEY is not configured. "
        "Please check backend/.env"
    )


ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 60


security = HTTPBearer()


# ============================================================
# REQUEST MODELS
# ============================================================

class RegisterRequest(BaseModel):

    name: str

    email: EmailStr

    password: str


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(
    password: str
) -> str:

    password_bytes = (
        password.encode("utf-8")
    )

    if len(password_bytes) > 72:

        raise ValueError(
            "Password must be 72 bytes or fewer."
        )

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(
        password_bytes,
        salt
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    password_bytes = (
        plain_password.encode("utf-8")
    )

    if len(password_bytes) > 72:

        return False

    return bcrypt.checkpw(
        password_bytes,
        hashed_password.encode("utf-8")
    )


# ============================================================
# JWT
# ============================================================

def create_access_token(
    user_id: int
) -> str:

    expire = (
        datetime.now(timezone.utc)
        +
        timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {

        "sub": str(user_id),

        "exp": expire

    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials =
        Depends(security),

    db: Session =
        Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get(
            "sub"
        )

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token."
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token."
        )

    try:

        user_id = int(user_id)

    except ValueError:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return user


# ============================================================
# REGISTER
# ============================================================

@router.post("/register")
def register(

    request: RegisterRequest,

    db: Session =
        Depends(get_db)

):

    existing_user = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail=(
                "A user with this email "
                "already exists."
            )
        )


    if len(
        request.password.encode("utf-8")
    ) < 6:

        raise HTTPException(
            status_code=400,
            detail=(
                "Password must contain "
                "at least 6 characters."
            )
        )


    try:

        password_hash = hash_password(
            request.password
        )

        user = User(

            name=request.name,

            email=request.email,

            password_hash=password_hash

        )

        db.add(user)

        db.commit()

        db.refresh(user)

        return {

            "status": "success",

            "user": {

                "id": user.id,

                "name": user.name,

                "email": user.email

            },

            "message":
                "Recruiter account created successfully."

        }

    except ValueError as error:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Registration failed: {str(error)}"
            )
        )


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(

    request: LoginRequest,

    db: Session =
        Depends(get_db)

):

    user = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    try:

        password_valid = verify_password(

            request.password,

            user.password_hash

        )

    except Exception:

        password_valid = False


    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )


    access_token = create_access_token(
        user.id
    )


    return {

        "status": "success",

        "access_token": access_token,

        "token_type": "bearer",

        "user": {

            "id": user.id,

            "name": user.name,

            "email": user.email

        }

    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get("/me")
def get_me(

    current_user: User =
        Depends(get_current_user)

):

    return {

        "status": "success",

        "user": {

            "id": current_user.id,

            "name": current_user.name,

            "email": current_user.email

        }

    }