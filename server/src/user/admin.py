from django.contrib import admin

from .models import Profile

admin.site.site_title = "Acad AI Admin"
admin.site.site_header = "Acad AI Admin"
admin.site.index_title = "Acad AI Admin"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "email_verified",
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
