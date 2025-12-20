# import cohere
from typing import List, Dict, Any
from src.config.settings import settings
from src.models.entities import BookContent


# class EmbeddingService:
#     def __init__(self):
#         self.client = cohere.Client(settings.cohere_api_key)
#         self.model = settings.cohere_embedding_model
        
#     def embed_documents(self, texts: List[str]) -> List[List[float]]:
#         response = self.client.embed(
#             texts=texts,
#             model=self.model,
#             input_type="search_document"
#         )
#         return response.embeddings

#     def embed_query(self, text: str) -> List[float]:
#         response = self.client.embed(
#             texts=[text],
#             model=self.model,
#             input_type="search_query"
#         )
#         return response.embeddings[0]

    
#     # def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
#     #     """Generate embeddings for a list of texts using Cohere"""
#     #     response = self.client.embed(
#     #         texts=texts,
#     #         model=self.model,
#     #         input_type="search_document"  # Using search_document for content chunks
#     #     )
#     #     return [embedding for embedding in response.embeddings]
        
#     def embed_book_content(self, book_contents: List[BookContent]) -> List[Dict[str, Any]]:
#         """Generate embeddings for book content chunks"""
#         # Extract the text content from each book content item
#         texts = [content.content for content in book_contents]
        
#         # Generate embeddings
#         embeddings = self.embed_documents(texts)

        
#         # Create result with embeddings and metadata
#         results = []
#         for i, content in enumerate(book_contents):
#             results.append({
#                 "id": content.chunk_id,
#                 "vector": embeddings[i],
#                 "payload": {
#                     "book_id": content.book_id,
#                     "chapter": content.chapter,
#                     "section": content.section,
#                     "paragraph_index": content.paragraph_index,
#                     "page_number": content.page_number,
#                     "content_type": content.content_type.value,
#                     "content": content.content,
#                     "chunk_id": content.chunk_id
#                 }
#             })
        
#         return results


# # Global instance
# embedding_service = EmbeddingService()
# import cohere
# from typing import List, Dict, Any
# from src.config.settings import settings
# from src.models.entities import BookContent


# class EmbeddingService:
#     def __init__(self):
#         self.client = cohere.Client(settings.cohere_api_key)
#         self.model = settings.cohere_embedding_model

#     # For indexing documents (book chunks)
#     def embed_documents(self, texts: List[str]) -> List[List[float]]:
#         response = self.client.embed(
#             texts=texts,
#             model=self.model,
#             input_type="search_document"
#         )
#         return response.embeddings

#     # For user queries
#     def embed_query(self, text: str) -> List[float]:
#         response = self.client.embed(
#             texts=[text],
#             model=self.model,
#             input_type="search_query"
#         )
#         return response.embeddings[0]

#     # Used during indexing
#     def embed_book_content(self, book_contents: List[BookContent]) -> List[Dict[str, Any]]:
#         texts = [content.content for content in book_contents]

#         embeddings = self.embed_documents(texts)

#         results = []
#         for i, content in enumerate(book_contents):
#             results.append({
#                 "id": content.chunk_id,
#                 "vector": embeddings[i],
#                 "payload": {
#                     "book_id": content.book_id,
#                     "chapter": content.chapter,
#                     "section": content.section,
#                     "paragraph_index": content.paragraph_index,
#                     "page_number": content.page_number,
#                     "content_type": content.content_type.value,
#                     "content": content.content,
#                     "chunk_id": content.chunk_id
#                 }
#             })
#         return results


# # ✅ SAFE global instance
# embedding_service = EmbeddingService()


import requests
from src.config.settings import settings

HF_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_EMBED_URL = (
    f"https://api-inference.huggingface.co/pipeline/feature-extraction/"
    f"{HF_EMBED_MODEL}"
)

class EmbeddingService:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.hf_api_token}",
            "Content-Type": "application/json"
        }

    def embed_text(self, text: str) -> list[float]:
        payload = {
            "inputs": text,
            "options": {
                "wait_for_model": True
            }
        }

        response = requests.post(
            HF_EMBED_URL,
            headers=self.headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        # Case 1: [[float, float, ...]]
        if isinstance(data, list) and isinstance(data[0], list) and isinstance(data[0][0], float):
            return data[0]

        # Case 2: [[[float]]] → mean pooling
        if (
            isinstance(data, list)
            and isinstance(data[0], list)
            and isinstance(data[0][0], list)
        ):
            vectors = data[0]
            dim = len(vectors[0])
            return [
                sum(token[i] for token in vectors) / len(vectors)
                for i in range(dim)
            ]

        raise ValueError(f"Unexpected embedding response: {data}")


embedding_service = EmbeddingService()
