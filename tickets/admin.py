from django.contrib import admin
from .models import *
# Register your models here.
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title','created_by','assigned_to', 'status', 'priority', )
    empty_value_display = '-empty-'
    list_filter = ('created_by', 'assigned_to', 'status')
    search_fields = ('title',)

class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket','parent','sender', 'message', 'attachment', )
    empty_value_display = '-empty-'
    list_filter = ('parent', 'ticket', 'sender')
    search_fields = ('message',)

class CloseRequestAdmin(admin.ModelAdmin):
    list_display = ('ticket','requested_by','approved' )
    empty_value_display = '-empty-'
    list_filter = ('approved', 'ticket', 'requested_by')
    actions = ['approve_requests']

    def approve_requests(self, request, queryset):
        queryset.update(approved=True)
    approve_requests.short_description = "Approve selected requests."

class StatusLogAdmin(admin.ModelAdmin):
    list_display = ('ticket','old_status','new_status','changed_by' )
    empty_value_display = '-empty-'
    list_filter = ('ticket','changed_by')

admin.site.register(Ticket,TicketAdmin)
admin.site.register(TicketMessage,TicketMessageAdmin)
admin.site.register(CloseRequest,CloseRequestAdmin)
admin.site.register(StatusLog,StatusLogAdmin)