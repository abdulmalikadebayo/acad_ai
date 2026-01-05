from rest_framework import serializers

from .models import Choice, Course, Exam, Question, Submission, SubmissionAnswer


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name", "code"]


class ChoicePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]


class QuestionPublicSerializer(serializers.ModelSerializer):
    choices = ChoicePublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "type", "prompt", "points", "order", "metadata", "choices"]


class ExamListSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "duration_minutes",
            "course",
            "metadata",
            "is_active",
            "starts_at",
            "ends_at",
        ]


class ExamDetailSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "duration_minutes",
            "course",
            "metadata",
            "is_active",
            "starts_at",
            "ends_at",
            "questions",
        ]


class SubmissionAnswerCreateSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_choice_id = serializers.IntegerField(required=False, allow_null=True)
    answer_text = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=5000
    )


class SubmissionCreateSerializer(serializers.Serializer):
    answers = SubmissionAnswerCreateSerializer(many=True)

    def validate_answers(self, answers):
        if not answers:
            raise serializers.ValidationError("Answers cannot be empty.")
        # Ensure no duplicate question_ids in payload
        qids = [a["question_id"] for a in answers]
        if len(qids) != len(set(qids)):
            raise serializers.ValidationError("Duplicate question_id found in answers.")
        return answers


class SubmissionListSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    course_code = serializers.CharField(source="exam.course.code", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "exam",
            "exam_title",
            "course_code",
            "status",
            "submitted_at",
            "graded_at",
            "score",
            "max_score",
            "grading_version",
        ]


class SubmissionAnswerResultSerializer(serializers.ModelSerializer):
    question_prompt = serializers.CharField(source="question.prompt", read_only=True)
    question_type = serializers.CharField(source="question.type", read_only=True)
    max_points = serializers.DecimalField(
        source="question.points", max_digits=6, decimal_places=2, read_only=True
    )
    selected_choice_text = serializers.CharField(
        source="selected_choice.text", read_only=True, default=""
    )

    class Meta:
        model = SubmissionAnswer
        fields = [
            "id",
            "question",
            "question_prompt",
            "question_type",
            "max_points",
            "answer_text",
            "selected_choice",
            "selected_choice_text",
            "is_correct",
            "awarded_points",
            "feedback",
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    exam = ExamListSerializer(read_only=True)
    answers = SubmissionAnswerResultSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "exam",
            "status",
            "submitted_at",
            "graded_at",
            "score",
            "max_score",
            "feedback",
            "grading_version",
            "answers",
        ]
