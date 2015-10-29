from django.contrib import admin
from .models import Message, Thread, MessageBox


class MessageAdmin(admin.ModelAdmin):
    model = Message
    date_hierarchy = 'date'
    search_field = ('text',)
    


class ThreadAdmin(admin.ModelAdmin):
    model = Thread
    list_display = ('title',)
    search_field = ('title',)


class MessageBoxAdmin(admin.ModelAdmin):
    model = MessageBox
    list_display = ('user', 'thread', 'is_read', 'status')
    date_hierarchy = 'date_read'



admin.site.register(MessageBox, MessageBoxAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message, MessageAdmin)
