from fastapi import HTTPException, status

INVALID_TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token error",
    headers={"WWW-Authenticate": "Bearer"},
)

INVALID_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
)

USER_NOT_FOUND_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
)

INVALID_TOKEN_TYPE_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
)
