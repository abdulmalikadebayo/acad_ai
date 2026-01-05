from django.contrib import admin

from .models import Choice, Course, Exam, Question, Submission, SubmissionAnswer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "type", "order", "points")
    list_filter = ("type", "exam")
    inlines = [ChoiceInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "duration_minutes",
        "is_active",
        "starts_at",
        "ends_at",
        "created_at",
    )
    list_filter = ("is_active", "course", "created_at")
    search_fields = ("title", "course__code", "course__name")
    readonly_fields = ("created_at",)
    date_hierarchy = "starts_at"
    ordering = ("-created_at",)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "text", "is_correct")
    list_filter = ("is_correct", "question__exam")
    search_fields = ("text", "question__prompt")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "exam",
        "status",
        "score",
        "max_score",
        "submitted_at",
        "graded_at",
    )
    list_filter = ("status", "exam", "submitted_at", "graded_at")
    search_fields = ("student__username", "student__email", "exam__title")
    readonly_fields = ("submitted_at", "graded_at")
    date_hierarchy = "submitted_at"
    ordering = ("-submitted_at",)


@admin.register(SubmissionAnswer)
class SubmissionAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "submission", "question", "is_correct", "awarded_points")
    list_filter = ("is_correct", "question__exam", "submission__status")
    search_fields = ("submission__student__username", "question__prompt", "answer_text")
    readonly_fields = ("submission", "question")
