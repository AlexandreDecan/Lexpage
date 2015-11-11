from django.contrib import admin
from .models import Message, Thread, MessageBox


class MessageAdmin(admin.ModelAdmin):  # pragma: no cover
    model = Message
    date_hierarchy = 'date'
    search_field = ('text',)


class ThreadAdmin(admin.ModelAdmin):  # pragma: no cover
    model = Thread
    list_display = ('title',)
    search_field = ('title',)


class MessageBoxAdmin(admin.ModelAdmin):  # pragma: no cover
    model = MessageBox
    list_display = ('user', 'thread', 'is_read', 'status')
    date_hierarchy = 'date_read'


admin.site.register(MessageBox, MessageBoxAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message, MessageAdmin)
