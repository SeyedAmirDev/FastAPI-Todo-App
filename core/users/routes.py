import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from datetime import timedelta, datetime

from core.database import get_db
from users.schemas import UserLoginSchema, RefreshTokenSchema, UserRegisterSchema
from users.models import UserModel, TokenModel
from auth.jwt_auth import (
    generate_access_token,
    generate_access_token_from_refresh,
    generate_refresh_token,
)


router = APIRouter(prefix="/users", tags=["Users"])

TOKEN_EXPIRATION_DAYS = 1


def generate_token(length: int = 32) -> str:
    """
    Generate a random token
    :param length: int
    :return: string
    """
    return secrets.token_hex(length)


def create_access_token(for_user: UserModel, db: Session) -> TokenModel:
    """
    This function utility create a random generated token
    for each user and persist that in database.

    :param for_user: UserModel
    :param db: Session
    :return: TokenModel object
    """
    user = for_user
    # generate random token
    new_token = generate_token()
    # evaluate expire time for token
    expiration = get_expiration_access_token()
    # create token object and then persist that in database
    token = TokenModel(
        user_id=user.id, token=new_token, expiration_date=expiration
    )
    db.add(token)
    db.commit()

    return token


def get_expiration_access_token():
    """
    getting expiration time for update or creating new token goal
    """
    expiration = datetime.now() + timedelta(minutes=TOKEN_EXPIRATION_DAYS)
    return expiration


def access_token_has_expired(token: TokenModel) -> bool:
    """
    check weather a token expired or not.

    :param token: TokenModel
    :return: bool
    """
    return token.expiration_date and token.expiration_date < datetime.now()


def set_new_access_token(token: TokenModel, db: Session) -> TokenModel:
    """
    regenerate new token for provided token object
    :param token: TokenModel
    :return: TokenModel
    """
    token.token = generate_token()
    token.expiration_date = get_expiration_access_token()
    db.commit()
    db.refresh(token)

    return token


def get_or_create_access_token(for_user: UserModel, db: Session) -> TokenModel:
    """
    This function utility whether get token or create new token
    :param user: UserModel
    :param db: Session
    :return: TokenModel
    """
    user = for_user

    token = db.query(TokenModel).filter_by(user_id=user.id).one_or_none()

    if not token:
        token = create_access_token(for_user=user, db=db)
    elif access_token_has_expired(token):
        token = set_new_access_token(token=token, db=db)

    return token


def get_user_by_username(username: str, db: Session) -> UserModel:
    """
    get user by username
    """
    user = db.query(UserModel).filter_by(username=username).one_or_none()
    return user


def authenticate_user(
    username: str, password: str, db: Session
) -> UserModel | None:
    """
    authenticate user by username and password
    :param username: str
    :param password: str
    :param db: Session
    :return: UserModel | None
    """
    user = get_user_by_username(username=username, db=db)
    if not user or not user.verify_password(password):
        return None

    return user


@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user = authenticate_user(request.username, request.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password.",
        )

    token = get_or_create_access_token(for_user=user, db=db)

    return JSONResponse(
        content={"detail": "Successfully logged in.", "token": token.token}
    )


@router.post("/jwt/login/")
async def user_login_jwt(
    request: UserLoginSchema, db: Session = Depends(get_db)
):
    user = authenticate_user(request.username, request.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user or password.",
        )

    access_token = generate_access_token(user.id)
    refresh_token = generate_refresh_token(user.id)

    return JSONResponse(
        content={
            "detail": "Successfully logged in.",
            "token": {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        }
    )


@router.post("/jwt/refresh/")
async def refresh_access_token(request: RefreshTokenSchema):
    new_access_token = generate_access_token_from_refresh(
        request.refresh_token
    )

    return JSONResponse(
        content={
            "detail": "Successfully refreshed access token.",
            "token": new_access_token,
        }
    )


@router.post("/register")
async def user_register(
    request: UserRegisterSchema, db: Session = Depends(get_db)
):
    user_exists = db.query(
        exists().where(UserModel.username == request.username)
    ).scalar()

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered.",
        )
    user = UserModel(username=request.username)
    user.set_password(request.password)
    db.add(user)
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"detail": "user registered successfully."},
    )
