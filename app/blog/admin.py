from django.contrib import admin
from .models import BlogPost


class PostAdmin(admin.ModelAdmin):  # pragma: no cover
    model = BlogPost
    list_display = ('title', 'tags', 'author', 'date_created', 'date_published', 'status')
    readonly_fields = ('status',)
    
    search_field = ('author__username', 'title', 'tags')
    date_hierarchy = 'date_published'
    
    list_editable = ('tags',)
    list_filter = ('status', )
    
    actions = ['approve', 'publish', 'hide']
    prepopulated_fields = {"slug": ("title",)}

    def approve(self, request, queryset):
        self._change_status(request, queryset, BlogPost.STATUS_APPROVED)
    approve.short_description = 'Valider les billets'

    def publish(self, request, queryset):
        self._change_status(request, queryset, BlogPost.STATUS_PUBLISHED)
    publish.short_description = 'Publier les billets'

    def hide(self, request, queryset):
        self._change_status(request, queryset, BlogPost.STATUS_HIDDEN)
    hide.short_description = 'Masquer les billets'

    def _change_status(self, request, queryset, status):
        for post in queryset:
            post.change_status(request.user, status)


admin.site.register(BlogPost, PostAdmin)
