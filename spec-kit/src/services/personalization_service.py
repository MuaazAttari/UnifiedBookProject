from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json

from src.models.personalization_profile import PersonalizationProfile
from src.models.user import UserBackgroundQuestionnaire
from src.schemas.personalization import PersonalizationProfileCreate, PersonalizationProfileUpdate


class PersonalizationService:
    """Service class for personalization functionality."""

    @staticmethod
    def get_personalization_profile(db: Session, user_id: str, chapter_id: str) -> Optional[PersonalizationProfile]:
        """
        Get a personalization profile for a specific user and chapter.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID

        Returns:
            PersonalizationProfile object or None if not found
        """
        return db.query(PersonalizationProfile).filter(
            PersonalizationProfile.user_id == user_id,
            PersonalizationProfile.chapter_id == chapter_id
        ).first()

    @staticmethod
    def create_personalization_profile(
        db: Session,
        user_id: str,
        chapter_id: str,
        profile_data: PersonalizationProfileCreate
    ) -> PersonalizationProfile:
        """
        Create a new personalization profile.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID
            profile_data: Personalization profile data

        Returns:
            Created PersonalizationProfile object
        """
        # Check if profile already exists
        existing_profile = db.query(PersonalizationProfile).filter(
            PersonalizationProfile.user_id == user_id,
            PersonalizationProfile.chapter_id == chapter_id
        ).first()

        if existing_profile:
            # Update existing profile instead of creating a new one
            return PersonalizationService.update_personalization_profile(
                db, user_id, chapter_id, profile_data
            )

        # Create new profile
        db_profile = PersonalizationProfile(
            user_id=user_id,
            chapter_id=chapter_id,
            difficulty_level=profile_data.difficulty_level,
            content_preferences=json.dumps(profile_data.content_preferences) if profile_data.content_preferences else None,
            learning_style=profile_data.learning_style,
            personalization_enabled=profile_data.personalization_enabled,
            custom_preferences=json.dumps(profile_data.custom_preferences) if profile_data.custom_preferences else None
        )

        db.add(db_profile)
        try:
            db.commit()
            db.refresh(db_profile)
        except IntegrityError:
            db.rollback()
            raise

        return db_profile

    @staticmethod
    def update_personalization_profile(
        db: Session,
        user_id: str,
        chapter_id: str,
        profile_data: PersonalizationProfileUpdate
    ) -> Optional[PersonalizationProfile]:
        """
        Update an existing personalization profile.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID
            profile_data: Personalization profile update data

        Returns:
            Updated PersonalizationProfile object or None if not found
        """
        db_profile = db.query(PersonalizationProfile).filter(
            PersonalizationProfile.user_id == user_id,
            PersonalizationProfile.chapter_id == chapter_id
        ).first()

        if not db_profile:
            return None

        # Update fields if provided
        if profile_data.difficulty_level is not None:
            db_profile.difficulty_level = profile_data.difficulty_level
        if profile_data.content_preferences is not None:
            db_profile.content_preferences = json.dumps(profile_data.content_preferences)
        if profile_data.learning_style is not None:
            db_profile.learning_style = profile_data.learning_style
        if profile_data.personalization_enabled is not None:
            db_profile.personalization_enabled = profile_data.personalization_enabled
        if profile_data.custom_preferences is not None:
            db_profile.custom_preferences = json.dumps(profile_data.custom_preferences)

        db.commit()
        db.refresh(db_profile)
        return db_profile

    @staticmethod
    def get_user_personalization_for_chapter(db: Session, user_id: str, chapter_id: str) -> Dict[str, Any]:
        """
        Get personalization settings for a user and chapter, with fallback to user questionnaire.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID

        Returns:
            Dictionary with personalization settings
        """
        # Get specific chapter personalization
        profile = PersonalizationService.get_personalization_profile(db, user_id, chapter_id)

        # Get user's background questionnaire for general preferences
        questionnaire = db.query(UserBackgroundQuestionnaire).filter(
            UserBackgroundQuestionnaire.user_id == user_id
        ).first()

        # Start with default settings
        result = {
            "difficulty_level": "intermediate",  # Default
            "content_preferences": {},
            "learning_style": "theoretical",  # Default
            "personalization_enabled": False,
            "custom_preferences": {}
        }

        # Apply questionnaire preferences as defaults
        if questionnaire:
            if questionnaire.experience_with_ai:
                result["difficulty_level"] = questionnaire.experience_with_ai
            elif questionnaire.experience_with_robotics:
                result["difficulty_level"] = questionnaire.experience_with_robotics

            if questionnaire.preferred_learning_style:
                result["learning_style"] = questionnaire.preferred_learning_style

        # Override with specific chapter preferences if available
        if profile:
            if profile.difficulty_level:
                result["difficulty_level"] = profile.difficulty_level
            if profile.content_preferences:
                try:
                    result["content_preferences"] = json.loads(profile.content_preferences)
                except:
                    pass  # Keep default if JSON parsing fails
            if profile.learning_style:
                result["learning_style"] = profile.learning_style
            if profile.personalization_enabled is not None:
                result["personalization_enabled"] = profile.personalization_enabled
            if profile.custom_preferences:
                try:
                    result["custom_preferences"] = json.loads(profile.custom_preferences)
                except:
                    pass  # Keep default if JSON parsing fails

        return result

    @staticmethod
    def adjust_content_for_user(
        db: Session,
        content: str,
        user_id: str,
        chapter_id: str
    ) -> str:
        """
        Adjust content based on user's personalization preferences.

        Args:
            db: Database session
            content: Original content
            user_id: User ID
            chapter_id: Chapter ID

        Returns:
            Adjusted content string
        """
        personalization = PersonalizationService.get_user_personalization_for_chapter(
            db, user_id, chapter_id
        )

        # If personalization is not enabled, return original content
        if not personalization.get("personalization_enabled", False):
            return content

        difficulty_level = personalization.get("difficulty_level", "intermediate")
        learning_style = personalization.get("learning_style", "theoretical")

        # Apply personalization based on difficulty level
        adjusted_content = content
        if difficulty_level == "beginner":
            # For beginners, add more explanations and examples
            adjusted_content = PersonalizationService._simplify_content(adjusted_content)
        elif difficulty_level == "advanced":
            # For advanced users, add more technical depth
            adjusted_content = PersonalizationService._add_technical_depth(adjusted_content)

        # Apply personalization based on learning style
        if learning_style == "visual":
            # Add visual element suggestions
            adjusted_content = PersonalizationService._add_visual_elements(adjusted_content)
        elif learning_style == "hands_on":
            # Add practical examples and exercises
            adjusted_content = PersonalizationService._add_practical_elements(adjusted_content)

        return adjusted_content

    @staticmethod
    def _simplify_content(content: str) -> str:
        """Simplify content for beginner users."""
        # This is a basic implementation - in a real system, this would use more sophisticated techniques
        # For now, we'll add explanations and break down complex concepts
        lines = content.split('\n')
        simplified_lines = []

        for line in lines:
            # Simplify complex terminology
            simplified_line = line.replace("algorithm", "step-by-step process")
            simplified_line = simplified_line.replace("implementation", "way to build")
            simplified_line = simplified_line.replace("optimization", "improvement")
            simplified_line = simplified_line.replace("abstraction", "simplified model")

            # Add beginner-friendly explanations
            if any(word in simplified_line.lower() for word in ["complex", "advanced", "sophisticated"]):
                simplified_line += " [Beginner note: This might seem complex at first, but it's just combining simpler concepts.]"

            simplified_lines.append(simplified_line)

        simplified_content = "\n".join(simplified_lines)
        return f"[Beginner-friendly version]\n\n{simplified_content}\n\n[Key takeaway: This concept is fundamental and will help you understand more advanced topics later.]"

    @staticmethod
    def _add_technical_depth(content: str) -> str:
        """Add technical depth for advanced users."""
        # This is a basic implementation - in a real system, this would use more sophisticated techniques
        lines = content.split('\n')
        enhanced_lines = []

        for line in lines:
            enhanced_line = line
            # Add technical depth to relevant concepts
            if "algorithm" in enhanced_line.lower():
                enhanced_line += " [Technical note: Consider time complexity O(n log n) and space complexity implications.]"
            elif "process" in enhanced_line.lower():
                enhanced_line += " [Technical note: This process can be parallelized for better performance.]"

            enhanced_lines.append(enhanced_line)

        enhanced_content = "\n".join(enhanced_lines)
        return f"{enhanced_content}\n\n[Advanced insight: This concept connects to related areas like computational complexity, system architecture, and performance optimization.]"

    @staticmethod
    def _add_visual_elements(content: str) -> str:
        """Add visual element suggestions."""
        # Identify key concepts that could benefit from visualization
        visual_suggestions = []
        if "process" in content.lower() or "algorithm" in content.lower():
            visual_suggestions.append("Flowchart or process diagram")
        if "structure" in content.lower() or "model" in content.lower():
            visual_suggestions.append("Diagram showing components and relationships")
        if "comparison" in content.lower() or "difference" in content.lower():
            visual_suggestions.append("Comparison table or Venn diagram")

        if visual_suggestions:
            return f"{content}\n\n*[Visual suggestion: Consider adding {', '.join(visual_suggestions)} to illustrate this concept]*"
        else:
            return f"{content}\n\n*[Visual suggestion: Consider adding a diagram or chart to illustrate this concept]*"

    @staticmethod
    def _add_practical_elements(content: str) -> str:
        """Add practical examples and exercises."""
        # Identify concepts that could benefit from hands-on practice
        practical_suggestions = []
        if "algorithm" in content.lower():
            practical_suggestions.append("Try implementing this algorithm with a small dataset")
        if "concept" in content.lower():
            practical_suggestions.append("Apply this concept to a real-world scenario")
        if "process" in content.lower():
            practical_suggestions.append("Walk through this process step-by-step with an example")

        if practical_suggestions:
            return f"{content}\n\n*[Hands-on suggestion: {'; '.join(practical_suggestions)}]*"
        else:
            return f"{content}\n\n*[Hands-on suggestion: Try implementing this concept with a practical exercise]*"

    @staticmethod
    def get_all_user_profiles(db: Session, user_id: str) -> list[PersonalizationProfile]:
        """
        Get all personalization profiles for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of PersonalizationProfile objects
        """
        return db.query(PersonalizationProfile).filter(
            PersonalizationProfile.user_id == user_id
        ).all()

    @staticmethod
    def delete_personalization_profile(db: Session, user_id: str, chapter_id: str) -> bool:
        """
        Delete a personalization profile.

        Args:
            db: Database session
            user_id: User ID
            chapter_id: Chapter ID

        Returns:
            True if deleted, False if not found
        """
        profile = db.query(PersonalizationProfile).filter(
            PersonalizationProfile.user_id == user_id,
            PersonalizationProfile.chapter_id == chapter_id
        ).first()

        if not profile:
            return False

        db.delete(profile)
        db.commit()
        return True