from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from db.db import is_valid_token

# Define Bearer token security scheme
auth_scheme = HTTPBearer()


# Dependency to validate authorization
async def authorize(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    valid = await is_valid_token(token)

    if not valid:  # Replace with proper token validation logic
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return token
