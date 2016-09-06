from django.contrib import admin
from microservices.models import Service


class ServiceAdmin(admin.ModelAdmin):
    actions = ["update_status"]

    search_fields = ["name"]
    list_display = ["name", "host", "is_available"]
    list_filter = ["is_available"]
    readonly_fields = ["name", "host", "is_available"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def update_status(self, request, queryset):
        services = queryset.all()

        for service in services:
            service.update_availability()

        if len(services) == 1:
            message_bit = "1 service was"
        else:
            message_bit = "%s services were" % len(services)

        self.message_user(request, "%s successfully updated." % message_bit)

    update_status.short_description = "Update the selected services' status"

admin.site.register(Service, ServiceAdmin)
