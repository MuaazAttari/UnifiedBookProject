import asyncio
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from ..config.settings import settings


class ContentGenerationService:
    """
    Service for generating textbook content using OpenAI API
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_textbook_outline(
        self,
        subject: str,
        educational_level: str,
        chapters_count: int = 10,
        settings: Optional[Dict] = None
    ) -> Dict:
        """
        Generate a textbook outline with chapters and sections
        """
        if settings is None:
            settings = {}

        # Get preferences from settings
        include_exercises = settings.get('include_exercises', True)
        include_summaries = settings.get('include_summaries', True)
        default_style = settings.get('default_style', 'academic')

        prompt = f"""
        Create a detailed textbook outline for "{subject}" at the {educational_level} level.
        The textbook should have {chapters_count} chapters.
        Style: {default_style}
        Include exercises: {'Yes' if include_exercises else 'No'}
        Include summaries: {'Yes' if include_summaries else 'No'}

        For each chapter, include 3-5 sections with appropriate educational content.
        Based on the settings, include {'exercises and summaries' if include_exercises and include_summaries
                else 'exercises only' if include_exercises
                else 'summaries only' if include_summaries
                else 'no exercises or summaries'} as appropriate.

        Return the result as a structured JSON object with the following format:

        {{
            "title": "Textbook title",
            "subject": "{subject}",
            "educational_level": "{educational_level}",
            "chapters": [
                {{
                    "position": 1,
                    "title": "Chapter title",
                    "sections": [
                        {{
                            "position": 1,
                            "title": "Section title",
                            "type": "CONTENT",  # CONTENT, SUMMARY, EXERCISE, KEY_POINT
                            "content": "Detailed content for this section"
                        }}
                    ]
                }}
            ]
        }}

        Make the content appropriate for {educational_level} students with proper explanations, examples, and {'exercises and summaries' if include_exercises and include_summaries else 'exercises' if include_exercises else 'summaries' if include_summaries else 'content'}.
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Create comprehensive textbook content that is accurate, engaging, and appropriate for the specified educational level."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            import json
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Error generating textbook outline: {e}")
            # Return a mock response in case of error
            return {
                "title": f"Introduction to {subject}",
                "subject": subject,
                "educational_level": educational_level,
                "chapters": [
                    {
                        "position": 1,
                        "title": f"Introduction to {subject}",
                        "sections": [
                            {
                                "position": 1,
                                "title": "Overview",
                                "type": "CONTENT",
                                "content": f"This chapter introduces the fundamental concepts of {subject}."
                            }
                        ]
                    }
                ]
            }

    async def generate_chapter_content(
        self,
        subject: str,
        chapter_title: str,
        educational_level: str,
        include_exercises: bool = True,
        include_summaries: bool = True
    ) -> str:
        """
        Generate detailed content for a specific chapter
        """
        prompt = f"""
        Write detailed content for the chapter titled "{chapter_title}" in a textbook about "{subject}".
        The content should be appropriate for {educational_level} level students.

        Include:
        - Clear explanations of key concepts
        - Examples and illustrations where appropriate
        - { 'Exercises with solutions' if include_exercises else 'No exercises' }
        - { 'Chapter summary' if include_summaries else 'No summary' }

        Make the content engaging, educational, and comprehensive.
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Write comprehensive, accurate, and engaging textbook content appropriate for the specified educational level."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating chapter content: {e}")
            return f"Content for chapter: {chapter_title}"

    async def generate_section_content(
        self,
        subject: str,
        chapter_title: str,
        section_title: str,
        educational_level: str,
        section_type: str = "CONTENT"
    ) -> str:
        """
        Generate content for a specific section
        """
        type_description = {
            "CONTENT": "detailed educational content with explanations and examples",
            "SUMMARY": "a concise summary of key points",
            "EXERCISE": "practice exercises with solutions",
            "KEY_POINT": "important concepts and takeaways"
        }.get(section_type, "detailed educational content")

        prompt = f"""
        Write {type_description} for the section titled "{section_title}"
        in the chapter "{chapter_title}" of a textbook about "{subject}".
        The content should be appropriate for {educational_level} level students.

        Keep the content focused and relevant to the section title.
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Write focused, accurate, and educational content appropriate for the specified educational level and section type."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating section content: {e}")
            return f"Content for section: {section_title}"

    async def improve_content(
        self,
        content: str,
        feedback: str,
        educational_level: str
    ) -> str:
        """
        Improve existing content based on feedback
        """
        prompt = f"""
        Improve the following educational content based on this feedback:

        Content: {content}

        Feedback: {feedback}

        The improved content should be appropriate for {educational_level} level students.
        Make the content more accurate, clear, and educational while addressing the feedback.
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content editor. Improve the content to make it more accurate, clear, and educational while addressing the provided feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error improving content: {e}")
            return content


# Singleton instance
content_generation_service = ContentGenerationService()