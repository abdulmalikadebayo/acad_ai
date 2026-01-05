from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Exam, Submission
from .selectors import get_exam_with_questions, get_submission_for_owner
from .serializers import (
    ExamDetailSerializer,
    ExamListSerializer,
    SubmissionCreateSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer,
)
from .services.submission_service import create_and_grade_submission


class ExamListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamListSerializer

    def get_queryset(self):
        return (
            Exam.objects.select_related("course")
            .filter(is_active=True)
            .order_by("-created_at")
        )


class ExamDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamDetailSerializer
    lookup_url_kwarg = "exam_id"

    def get_object(self):
        return get_exam_with_questions(self.kwargs["exam_id"])


class SubmissionCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubmissionCreateSerializer

    def post(self, request, exam_id: int):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = create_and_grade_submission(
            user_id=request.user.id,
            exam_id=exam_id,
            answers_payload=serializer.validated_data["answers"],
        )
        return Response(
            SubmissionDetailSerializer(result.submission).data,
            status=status.HTTP_201_CREATED,
        )


class SubmissionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubmissionListSerializer

    def get_queryset(self):
        return (
            Submission.objects.select_related("exam", "exam__course")
            .filter(student_id=self.request.user.id)
            .order_by("-submitted_at")
        )


class SubmissionDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubmissionDetailSerializer
    lookup_url_kwarg = "submission_id"

    def get_object(self):
        return get_submission_for_owner(
            self.kwargs["submission_id"], self.request.user.id
        )
