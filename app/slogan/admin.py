from django.contrib import admin
from django.forms.widgets import TextInput
from django.db.models import TextField
from .models import Slogan


class SloganAdmin(admin.ModelAdmin):
    # actions = ('make_visible', 'make_invisible', )
    model = Slogan
    list_display = ('author', 'slogan', 'date', 'is_visible')
    search_fields = ('slogan', )
    date_hierarchy = 'date'
    list_filter = ('is_visible',)
    list_editable = ('slogan', 'is_visible',)

    formfield_overrides = {
        TextField: {'widget': TextInput},
    }

    def make_visible(self, request, queryset):
        self._set_visibility(request, queryset, True)
    make_visible.short_description = 'Rendre visible'

    def make_invisible(self, request, queryset):
        self._set_visibility(request, queryset, False)
    make_invisible.short_description = 'Rendre invisible'

    def _set_visibility(self, request, queryset, visible):
        queryset.update(is_visible=visible)


admin.site.register(Slogan, SloganAdmin)
