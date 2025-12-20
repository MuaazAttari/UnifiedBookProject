from fastapi import Request
from logging import getLogger, INFO, Formatter, StreamHandler
from datetime import datetime
import traceback
import sys


class LoggingMiddleware:
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logger = getLogger("rag_chatbot")
        logger.setLevel(INFO)
        
        # Avoid adding multiple handlers if logger already exists
        if not logger.handlers:
            handler = StreamHandler(sys.stdout)
            formatter = Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def __call__(self, request: Request, call_next):
        start_time = datetime.utcnow()
        
        # Log request
        self.logger.info(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Add processing time to response headers
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            self.logger.info(
                f"Response: {response.status_code} in {process_time:.2f}s"
            )
            
            return response
        except Exception as e:
            # Calculate processing time for error case
            process_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Log error
            self.logger.error(
                f"Error in request {request.method} {request.url}: {str(e)}",
                extra={
                    "traceback": traceback.format_exc(),
                    "process_time": process_time
                }
            )
            
            # Re-raise the exception to be handled by FastAPI
            raise