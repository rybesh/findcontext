from main.models import Resource, Package, LogRecord
from django.contrib import admin

class LogRecordAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'message')

admin.site.register(Resource)
admin.site.register(Package)
admin.site.register(LogRecord, LogRecordAdmin)
