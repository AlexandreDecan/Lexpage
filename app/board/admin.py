from django.contrib import admin
from .models import Message, Thread, Flag, MessageHistory


class MessageAdmin(admin.ModelAdmin):  # pragma: no cover
    model = Message
    date_hierarchy = 'date'
    search_field = ('text',)
    


class ThreadAdmin(admin.ModelAdmin):  # pragma: no cover
    model = Thread
    date_hierarchy = 'date_created'
    search_field = ('title',)


class FlagAdmin(admin.ModelAdmin):  # pragma: no cover
    model = Flag
    list_display = ('user', 'thread', 'message')


class MessageHistoryAdmin(admin.ModelAdmin):  # pragma: no cover
    model = MessageHistory
    list_display = ('edited_by', 'message', 'date')

admin.site.register(Flag, FlagAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageHistory, MessageHistoryAdmin)
