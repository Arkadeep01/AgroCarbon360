## backend/src/utils/responses.py

from fastapi.responses import JSONResponse

def success_response(message: str, data: dict = None, status_code=200):
    return JSONResponse(
        content={
            "success": True, 
            "data": data or {},
            "message": message
        }, 
        status_code=status_code
    )

def error_response(message: str, status_code: int = 400):
    """Standardized error response."""
    return JSONResponse(
        content={
            "success": False, 
            "error": message
        }, 
        status_code=status_code
    )
