from rest_framework.permissions import BasePermission


class IsOwnerOfSubmission(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return getattr(obj, "student_id", None) == request.user.id
