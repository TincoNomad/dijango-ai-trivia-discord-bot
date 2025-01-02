"""
Trivia Serializers Module

This module provides serializers for trivia-related models.
Includes serializers for:
- Trivia creation and updates
- Theme management
- Question handling
- Answer validation

Features:
- Data validation
- Nested serialization
- Custom field handling
"""

from rest_framework import serializers

from api.utils.jwt_utils import get_user_id_by_username

from .models import Answer, Question, Theme, Trivia


class ThemeSerializer(serializers.ModelSerializer):
    """
    Serializer for Theme model.
    Handles basic theme data.
    """

    class Meta:
        model = Theme
        fields = ["id", "name"]


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for Answer model.

    Features:
    - Optional ID field for updates
    - Answer validation
    """

    id = serializers.IntegerField(required=False)

    class Meta:
        model = Answer
        fields = ["id", "answer_title", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model.

    Features:
    - Nested answer handling
    - Points calculation
    - Question validation
    """

    id = serializers.IntegerField(required=False)
    answers = AnswerSerializer(many=True)
    points = serializers.IntegerField(default=10, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question_title", "points", "answers"]


class TriviaListSerializer(serializers.ModelSerializer):
    """
    Serializer for trivia list endpoint.

    Features:
    - Basic trivia information
    - Theme name resolution
    - Creator UUID handling

    Used in:
    - GET /api/trivias/ endpoint
    - List view responses
    """

    theme = serializers.CharField(source="theme.name")
    created_by = serializers.UUIDField(source="created_by.id", read_only=True)

    class Meta:
        model = Trivia
        fields = [
            "id",
            "title",
            "difficulty",
            "theme",
            "is_public",
            "created_by",
        ]


class TriviaSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed trivia information.

    Features:
    - Complete trivia data
    - Nested questions and answers
    - Theme handling
    - Permission checking
    - Creation tracking

    Used in:
    - GET /api/trivias/{id}/ endpoint
    - Detail view responses
    - Trivia creation/updates
    """

    theme = serializers.CharField(max_length=100)
    questions = QuestionSerializer(many=True, required=True)
    can_make_private = serializers.SerializerMethodField()
    username = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Trivia
        fields = [
            "id",
            "title",
            "is_public",
            "difficulty",
            "theme",
            "url",
            "created_by",
            "created_at",
            "questions",
            "can_make_private",
            "username",
        ]

    def validate(self, data):
        """
        Validate trivia data.

        Args:
            data: The data to validate

        Returns:
            dict: Validated data

        Raises:
            ValidationError: If user not found
        """
        username = data.get("username")
        if username:
            user_id = get_user_id_by_username(username)
            if not user_id:
                raise serializers.ValidationError(
                    {"username": "No user exists with this username"}
                )
        return data

    def validate_questions(self, value):
        """
        Validate questions data.

        Args:
            value: Questions data to validate

        Returns:
            list: Validated questions data

        Raises:
            ValidationError: If validation fails
        """
        if len(value) < 3:
            raise serializers.ValidationError("A trivia must have at least 3 questions")

        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 questions allowed")

        for question in value:
            if "answers" not in question or len(question["answers"]) < 2:
                raise serializers.ValidationError(
                    f"The question '{question.get('question_title', '')}'",
                    " must have at least 2 answers",
                )

            if len(question["answers"]) > 5:
                raise serializers.ValidationError(
                    f"The question '{question.get('question_title', '')}'",
                    "can have maximum 5 answers",
                )

            correct_answers = [
                answer
                for answer in question["answers"]
                if answer.get("is_correct", False)
            ]
            if not correct_answers:
                raise serializers.ValidationError(
                    f"The question '{question.get('question_title', '')}'",
                    " must have at least one correct answer",
                )

        return value

    def validate_title(self, value):
        """
        Validate trivia title uniqueness.

        Args:
            value: Title to validate

        Returns:
            str: Validated title

        Raises:
            ValidationError: If title already exists
        """
        if Trivia.objects.filter(title=value).exists():
            raise serializers.ValidationError(
                "A trivia with this title already exists. Please choose another title."
            )
        return value

    def get_can_make_private(self, obj):
        """
        Check if user can make trivia private.

        Args:
            obj: Trivia instance

        Returns:
            bool: True if user can make private
        """
        request = self.context.get("request")
        return request and request.user.is_authenticated

    def create(self, validated_data):
        """Create trivia with nested data"""
        questions_data = validated_data.pop("questions", [])
        theme_data = validated_data.pop("theme", None)
        validated_data.pop("username", None)
        theme = None

        if theme_data:
            if isinstance(theme_data, int):
                theme = Theme.objects.get(id=theme_data)
            else:
                theme, _ = Theme.objects.get_or_create(name=theme_data)

        trivia = Trivia.objects.create(theme=theme, **validated_data)

        # Create questions and answers
        for question_data in questions_data:
            answers_data = question_data.pop("answers", [])
            question = Question.objects.create(trivia=trivia, **question_data)

            for answer_data in answers_data:
                Answer.objects.create(question=question, trivia=trivia, **answer_data)

        return trivia

    def update(self, instance, validated_data):
        """Update trivia and related data"""
        questions_data = validated_data.pop("questions", None)
        theme_data = validated_data.pop("theme", None)

        # Handle theme update
        if theme_data:
            if (
                isinstance(theme_data, (int, str)) and len(str(theme_data)) == 36
            ):  # UUID length
                try:
                    theme = Theme.objects.get(id=theme_data)
                except Theme.DoesNotExist:
                    raise serializers.ValidationError(
                        {"theme": "Theme with this ID does not exist"}
                    )
            else:
                # If theme_data is a string (name), get or create the theme
                theme, _ = Theme.objects.get_or_create(name=theme_data)
            validated_data["theme"] = theme

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update relationships
        if questions_data:
            self.update_questions(instance, questions_data)

        instance.save()
        return instance

    def update_questions(self, instance, questions_data):
        """Update questions and their answers"""
        for question_data in questions_data:
            question_id = question_data.get("id")
            if question_id:
                question = Question.objects.get(id=question_id, trivia=instance)
                for attr, value in question_data.items():
                    if attr != "answers":
                        setattr(question, attr, value)
                question.save()
                if "answers" in question_data:
                    self.update_answers(question, question_data["answers"])
            else:
                new_question = Question.objects.create(trivia=instance, **question_data)
                if "answers" in question_data:
                    self.create_answers(new_question, question_data["answers"])

    def update_answers(self, question, answers_data):
        """Update answers for a question"""
        for answer_data in answers_data:
            answer_id = answer_data.get("id")
            if answer_id:
                answer = Answer.objects.get(id=answer_id, question=question)
                for attr, value in answer_data.items():
                    setattr(answer, attr, value)
                answer.save()
            else:
                Answer.objects.create(question=question, **answer_data)
