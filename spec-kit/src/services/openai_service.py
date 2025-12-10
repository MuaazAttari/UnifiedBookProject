import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import openai
from openai import AsyncOpenAI

from src.config import settings


@dataclass
class ChatResponse:
    """Data class to represent a chat response."""
    content: str
    tokens_used: int
    model: str
    finish_reason: str


class OpenAIService:
    """Service class for OpenAI integration."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)

    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> ChatResponse:
        """
        Get completion from OpenAI API.

        Args:
            messages: List of messages in the conversation
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            ChatResponse object with content and metadata
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            if stream:
                # Handle streaming response
                content = ""
                async for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                tokens_used = len(content.split())  # Rough estimation
            else:
                # Handle non-streaming response
                content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else len(content.split())

            return ChatResponse(
                content=content or "",
                tokens_used=tokens_used,
                model=model,
                finish_reason=response.choices[0].finish_reason if response.choices else "stop"
            )

        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in OpenAI service: {str(e)}")
            raise

    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002"
    ) -> List[List[float]]:
        """
        Generate embeddings for the given texts.

        Args:
            texts: List of texts to embed
            model: OpenAI embedding model to use

        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=model
            )

            embeddings = []
            for item in response.data:
                embeddings.append(item.embedding)

            return embeddings

        except openai.APIError as e:
            self.logger.error(f"OpenAI embedding API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in OpenAI embedding service: {str(e)}")
            raise

    async def get_answer_from_context(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> ChatResponse:
        """
        Get an answer based on a query and provided context.

        Args:
            query: User's question
            context: Context to use for answering
            system_prompt: Optional system prompt to guide the response

        Returns:
            ChatResponse object with the answer
        """
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant for a Physical AI and Humanoid Robotics textbook. "
                "Use the provided context to answer questions. If the context doesn't contain "
                "the information needed to answer, say so clearly. Be concise and accurate."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"}
        ]

        return await self.get_completion(
            messages=messages,
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=500
        )

    async def summarize_text(
        self,
        text: str,
        max_length: int = 100
    ) -> ChatResponse:
        """
        Summarize a given text.

        Args:
            text: Text to summarize
            max_length: Maximum length of the summary in words

        Returns:
            ChatResponse object with the summary
        """
        system_prompt = f"You are a text summarization assistant. Create a concise summary of the given text in no more than {max_length} words."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        return await self.get_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=max_length * 3  # Rough estimation: 3 tokens per word
        )

    async def classify_text(
        self,
        text: str,
        categories: List[str]
    ) -> ChatResponse:
        """
        Classify text into one of the provided categories.

        Args:
            text: Text to classify
            categories: List of possible categories

        Returns:
            ChatResponse object with the classification
        """
        system_prompt = (
            f"You are a text classification assistant. Classify the given text into one of these categories: "
            f"{', '.join(categories)}. Respond with just the category name."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        return await self.get_completion(
            messages=messages,
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=20
        )

    async def extract_entities(
        self,
        text: str
    ) -> ChatResponse:
        """
        Extract named entities from the text.

        Args:
            text: Text to extract entities from

        Returns:
            ChatResponse object with extracted entities
        """
        system_prompt = (
            "You are an entity extraction assistant. Extract named entities from the given text. "
            "Return them in JSON format with entity type and value."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        return await self.get_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=300
        )

    async def validate_api_key(self) -> bool:
        """
        Validate the OpenAI API key by making a simple test request.

        Returns:
            True if API key is valid, False otherwise
        """
        try:
            await self.client.models.list()
            return True
        except openai.AuthenticationError:
            return False
        except Exception as e:
            self.logger.error(f"Error validating OpenAI API key: {str(e)}")
            return False


# Global instance
openai_service = OpenAIService()