from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db

from users.models import TokenModel
from users.routes import access_token_has_expired

security = HTTPBearer(scheme_name="Token")


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = (
        db.query(TokenModel)
        .filter_by(token=credentials.credentials)
        .one_or_none()
    )
    if not token or access_token_has_expired(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed.",
        )

    user = token.user

    return user
