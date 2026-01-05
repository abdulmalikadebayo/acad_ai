from django.urls import path

from .views import (
    ExamDetailView,
    ExamListView,
    SubmissionCreateView,
    SubmissionDetailView,
    SubmissionListView,
)

urlpatterns = [
    path("exams/", ExamListView.as_view(), name="exam-list"),
    path("exams/<int:exam_id>/", ExamDetailView.as_view(), name="exam-detail"),
    path(
        "exams/<int:exam_id>/submissions/",
        SubmissionCreateView.as_view(),
        name="submission-create",
    ),
    path("submissions/", SubmissionListView.as_view(), name="submission-list"),
    path(
        "submissions/<int:submission_id>/",
        SubmissionDetailView.as_view(),
        name="submission-detail",
    ),
]
