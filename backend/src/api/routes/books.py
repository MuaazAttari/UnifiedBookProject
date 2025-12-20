# from fastapi import APIRouter
# from typing import List
# from src.models.entities import BookContent, BookMetadata
# from src.services.book_service import book_service
# from src.services.ingestion_service import index_physical_ai_book

# router = APIRouter()

# @router.get("/books/{book_id}", response_model=BookMetadata)
# async def get_book_metadata(book_id: str):
#     """Retrieve metadata about a specific book"""
#     metadata = await book_service.get_book_metadata(book_id)
#     if not metadata:
#         from fastapi import HTTPException
#         raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
#     return metadata

# @router.post("/books/index")
# async def index_book_from_frontend(
#     book_id: str,
#     contents: List[str]
# ):
#     """Original endpoint for indexing content sent from frontend"""
#     book_contents = []

#     for i, text in enumerate(contents):
#         book_contents.append(
#             BookContent(
#                 book_id=book_id,
#                 chapter="",
#                 section="",
#                 paragraph_index=i,
#                 page_number=0,
#                 content_type=BookContentType.TEXT,
#                 content=text,
#                 chunk_id=f"{book_id}_{uuid.uuid4()}"
#             )
#         )

#     await book_service.index_book_content(book_contents)

#     return {
#         "status": "success",
#         "chunks_indexed": len(book_contents)
#     }

# @router.post("/books/index-md")
# async def index_book_from_markdown(book_id: str = "physical-ai-book"):
#     """New endpoint to index book content from Docusaurus markdown files"""
#     try:
#         await index_physical_ai_book(book_id)
#         return {
#             "status": "success",
#             "message": f"Book {book_id} indexed successfully from markdown files"
#         }
#     except Exception as e:
#         from fastapi import HTTPException
#         raise HTTPException(status_code=500, detail=f"Error indexing book from markdown: {str(e)}")
