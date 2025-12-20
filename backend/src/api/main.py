# from fastapi import FastAPI
# from contextlib import asynccontextmanager
# from src.config.settings import settings
# from src.api.routes import chat, health, books


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup logic
#     print("Starting up RAG Chatbot API...")
#     # Initialize services, connect to databases, etc.
#     yield
#     # Shutdown logic
#     print("Shutting down RAG Chatbot API...")
#     # Cleanup resources, close connections, etc.


# def create_app():
#     """Create and configure the FastAPI application"""
#     app = FastAPI(
#         title=settings.app_name,
#         version=settings.app_version,
#         description="RAG Chatbot API for book content",
#         lifespan=lifespan,
#         debug=settings.debug
#     )

#     # Include API routes
#     app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
#     app.include_router(health.router, prefix="/api/v1", tags=["health"])
#     app.include_router(books.router, prefix="/api/v1", tags=["books"])

#     return app


# # Create the main app instance
# app = create_app()


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "src.api.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level=settings.log_level.lower()
#     )



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.settings import settings
from src.api.routes import chat, health, books
# from src.api.routes.books import router as books_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up RAG Chatbot API...")
    yield
    print("Shutting down RAG Chatbot API...")


def create_app():
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="RAG Chatbot API for book content",
        lifespan=lifespan,
        debug=settings.debug
    )
    


    # 🔥 CORS (MANDATORY FOR FRONTEND)
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=["http://localhost:3000"],
        allow_origins=["*"],

        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(chat.router, prefix="/api/routes", tags=["chat"])
    app.include_router(health.router, prefix="/api/routes", tags=["health"])
    # app.include_router(books.router, prefix="/api/routes", tags=["books"])

    @app.get("/")
    async def root():
        return {
            "status": "OK",
            "message": "RAG Chatbot API is running"
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        # "src.api.main:app",
        "main:app",

        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
