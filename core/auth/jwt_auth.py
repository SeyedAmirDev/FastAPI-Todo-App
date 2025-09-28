from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.database import get_db
from sqlalchemy.orm import Session

from datetime import datetime
import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError, ExpiredSignatureError, InvalidAlgorithmError
from users.models import UserModel
from core.config import settings


ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

DEFAULT_JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 7  # default 7 days
DEFAULT_JWT_ACCESS_TOKEN_EXPIRES = 60 * 5  # default 5 minutes

security = HTTPBearer()


def unauthorized_exception(message: str) -> HTTPException:
    """
    Exception handler for unauthorized requests
    :param message: str
    :return: HTTPException
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message
    )


def jwt_token_has_expired(jwt_payload: dict) -> bool:
    """
    Check whether a token has expired.
    Returns True if expired, False otherwise.
    """
    exp = jwt_payload.get('exp')
    if not exp:
        return False

    return datetime.now() > datetime.fromtimestamp(exp)


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:
    """
    this function gives user token and authorize that
    :param credentials: HTTPAuthorizationCredentials
    :param db: Session
    :return: UserModel
    """
    token = credentials.credentials
    token_payload = validate_jwt_token(token)
    user_id = token_payload.get("user_id", None)

    if not user_id:
        raise unauthorized_exception(
            message="user_id not found in the payload."
        )

    # Defensive expiration check; PyJWT normally handles this.
    if jwt_token_has_expired(token_payload):
        raise unauthorized_exception(
            message="Expired token.",
        )

    # Check the token type to ensure it's an access token.
    if token_payload.get("type") != ACCESS_TOKEN_TYPE:
        raise unauthorized_exception(
            message="Invalid token type.",
        )

    user = db.query(UserModel).filter_by(id=user_id).one_or_none()

    if not user:
        raise unauthorized_exception(
            message='user not found.'
        )
    return user


def validate_jwt_token(token: str) -> dict:
    """
    Decode and validate a JWT token, raising HTTPException for errors.
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload

    except InvalidAlgorithmError as e:
        raise unauthorized_exception("Invalid algorithm specified.") from e
    except ExpiredSignatureError as e:
        raise unauthorized_exception("Token has expired.") from e
    except (DecodeError, InvalidSignatureError) as e:
        raise unauthorized_exception("Invalid token.") from e
    except Exception as e:
        raise unauthorized_exception(f"Authentication failed: {e}") from e


def generate_access_token(user_id: int, expired_at: int | None = None) -> str:
    """
    Generate a JWT access token for a given user.
    """
    now_ts = int(datetime.now().timestamp())

    if expired_at is None:
        try:
            expired_at = settings.JWT_ACCESS_TOKEN_EXPIRES
        except AttributeError:
            expired_at = DEFAULT_JWT_ACCESS_TOKEN_EXPIRES

    payload = {
        "user_id": user_id,
        "iat": now_ts,
        "exp": now_ts + expired_at,
        "type": ACCESS_TOKEN_TYPE,
    }

    return jwt.encode(payload, key=settings.JWT_SECRET_KEY,
                      algorithm=settings.JWT_ALGORITHM)


def generate_refresh_token(user_id: int, expired_at: int | None = None) -> str:
    """
    Generate a JWT refresh token for a given user.
    """
    now_ts = int(datetime.now().timestamp())

    if expired_at is None:
        try:
            expired_at = settings.JWT_REFRESH_TOKEN_EXPIRES
        except AttributeError:
            expired_at = DEFAULT_JWT_REFRESH_TOKEN_EXPIRES

    payload = {
        "user_id": user_id,
        "iat": now_ts,
        "exp": now_ts + expired_at,
        "type": REFRESH_TOKEN_TYPE,
    }

    return jwt.encode(payload, key=settings.JWT_SECRET_KEY,
                      algorithm=settings.JWT_ALGORITHM)


def generate_access_token_from_refresh(refresh: str):
    """
    Generate a new refresh token from a valid refresh token.
    """

    payload = validate_jwt_token(refresh)
    user_id = payload.get("user_id")

    if not user_id:
        raise unauthorized_exception("user_id not found in the payload.")

    if jwt_token_has_expired(payload):
        raise unauthorized_exception("Expired token.")

    if payload.get("type") != REFRESH_TOKEN_TYPE:
        raise unauthorized_exception("Invalid token type.")

    return generate_access_token(user_id)
