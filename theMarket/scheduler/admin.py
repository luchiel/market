from django.contrib import admin
from scheduler.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'signal', 'timestamp', 'is_pending']

admin.site.register(Event, EventAdmin)
