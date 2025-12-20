# import cohere
# from typing import List, Dict, Any
# from src.models.entities import RetrievedChunk, UserQuery
# from src.config.settings import settings

# # ===============================================

# print("COHERE KEY:", settings.cohere_api_key)
# # ===============================================
# class GenerationService:
#     def __init__(self):
#         self.client = cohere.Client(settings.cohere_api_key)
#         self.model = settings.cohere_model
    
#     def generate_response(self, 
#                          query_text: str, 
#                          retrieved_chunks: List[RetrievedChunk],
#                          selected_text: str = None) -> str:
#         """Generate a response based on query and retrieved context or selected text"""
        
#         # Determine the context to use
#         if selected_text:
#             # Use selected text as context
#             context = f"Based only on the following text: {selected_text}"
#         elif retrieved_chunks:
#             # Use retrieved chunks as context
#             context_parts = [f"Relevant information: {chunk['content']}" for chunk in retrieved_chunks]
#             context = "\n\n".join(context_parts)
#         else:
#             # No context available
#             return "This information is not available in the book."

#         # Construct the prompt
#         prompt = f"""
#         {context}

#         Question: {query_text}

#         Please provide a clear, accurate answer based only on the provided information.
#         If the information is not available in the provided text, respond with: "This information is not available in the book."
#         """
# # ==========================================================================================

#         # Generate response using Cohere
#         # response = self.client.generate(
#         #     model=self.model,
#         #     prompt=prompt,
#         #     max_tokens=500,
#         #     temperature=0.1,  # Low temperature for more consistent answers
#         #     stop_sequences=["Question:", "\n\n"]
#         # )

#         # # Extract and return the generated text
#         # generated_text = response.generations[0].text.strip()

#         # # Ensure we don't hallucinate by checking if the response is based on provided context
#         # if not generated_text or generated_text == "This information is not available in the book.":
#         #     return generated_text

#         # # If using selected text, add an indicator
#         # if selected_text:
#         #     return f"(Based on selected text only) {generated_text}"

#         # return generated_text
# # ==========================================================================================
#         # response = self.client.chat(
#         #     model="command-r-plus",
#         #     message=prompt
#         # )

#         # return response.text
# # ==========================================================================================


#         response = self.client.chat(
#             model="command",    # Cohere new chat model
#             messages=[
#                 {"role": "system", "content": "You are a book assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=500
#         )
#         return response.choices[0].message["content"]


# # Global instance
# generation_service = GenerationService()

# import cohere
# from src.config.settings import settings

# class GenerationService:
#     def __init__(self):
#         self.client = cohere.Client(settings.cohere_api_key)

#     def generate_response(self, query_text: str, retrieved_chunks=None, selected_text=None):
#         # Build context
#         if selected_text:
#             context = selected_text
#         elif retrieved_chunks:
#             context = "\n\n".join([c["content"] for c in retrieved_chunks])
#         else:
#             context = ""

#         prompt = f"""
# You are a helpful book assistant.
# Use ONLY the context below to answer the question.
# If not in context, say "This information is not available in the book."

# CONTEXT:
# {context}

# QUESTION:
# {query_text}

# ANSWER:
# """

#         response = self.client.chat(
#             model="command",   # <-- Cohere Chat API model
#             messages=prompt,
#             temperature=0.3,
#             max_tokens=400
#         )

#         # return response.choices[0].message["content"].strip()
#         return response.text.strip()

# generation_service = GenerationService()
# =============================================================
# import requests
# from src.config.settings import settings
# HF_MODEL = "google/flan-t5-large"
# HF_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"



# class GenerationService:
#     def __init__(self):
#         self.headers = {
#             "Authorization": f"Bearer {settings.hf_api_token}",
#             "Content-Type": "application/json"
#         }

#     def generate_response(self, query_text: str, context: str = ""):
#         payload = {
#             "inputs": f"""
#     You are a helpful book assistant.
#     Use ONLY the context below to answer.
#     If not present, say "This information is not available in the book."

#     CONTEXT:
#     {context}

#     QUESTION:
#     {query_text}

#     ANSWER:
#     """
#         }

#         response = requests.post(
#             HF_URL,
#             headers=self.headers,
#             json=payload,
#             timeout=60
#         )

#         response.raise_for_status()

#         data = response.json()

#         if isinstance(data, list):
#             return data[0]["generated_text"].strip()

#         return "No response generated"
# generation_service = GenerationService()
# =====================================================


# =========================================================
from groq import Groq
from src.config.settings import settings

class GenerationService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)

    def generate_response(self, query_text: str, context: str = ""):
        prompt = f"""
You are a helpful book assistant.
Use ONLY the context below to answer.
If the answer is not present, say:
"This information is not available in the book."

CONTEXT:
{context}

QUESTION:
{query_text}

ANSWER:
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=400
        )

        return response.choices[0].message.content.strip()


generation_service = GenerationService()

# =========================================================
# =========================================================
# import requests

# class GenerationService:

#     def generate_response(
#         self,
#         query_text: str,
#         retrieved_chunks=None,
#         context=None,
#         selected_text=None
#     ):

#         if context:
#             prompt = f"""
# You are an AI assistant answering questions from a book.

# BOOK CONTENT:
# {context}

# QUESTION:
# {query_text}

# Answer clearly and accurately using ONLY the book content.
# """
#         elif selected_text:
#             prompt = f"""
# TEXT:
# {selected_text}

# QUESTION:
# {query_text}
# """
#         else:
#             prompt = query_text

#         response = requests.post(
#             "http://localhost:11434/api/generate",
#             json={
#                 "model": "qwen2.5",
#                 "prompt": prompt,
#                 "stream": False
#             },
#             timeout=120
#         )

#         response.raise_for_status()
#         return response.json()["response"]


# generation_service = GenerationService()
