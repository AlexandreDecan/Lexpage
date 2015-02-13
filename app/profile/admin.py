#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import Profile, ActiveUser, ActivationKey


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'country', 'birthdate', 'last_visit',)
    search_fields = ('user', 'country',)
    date_hierarchy = 'last_visit'

class InlineProfileAdmin(admin.StackedInline):
    model = Profile
    can_delete = False
    

class UserAdmin(UserAdmin):
    inlines = (InlineProfileAdmin,)
    list_display = ('username', 'email', 'date_joined', 'last_login', 'is_active')
    list_filter = ('is_active', 'is_staff')
    search_fields = ['username', 'email']
    date_hierarchy = 'date_joined'


class ActivationKeyAdmin(admin.ModelAdmin):
    actions = ['activate_users', 'resend_activation_email', 'clean', 'revoke']
    list_display = ('user', 'has_expired')
    raw_id_fields = ['user']
    search_fields = ('user__username', 'user__email')

    def activate_users(self, request, queryset):
        """
        Activates the selected users, if they are not already
        activated.
        """
        for profile in queryset:
            ActivationKey.objects.activate_user(profile.key)
    activate_users.short_description = 'Activer les comptes'


    def clean(self, request, queryset):
        """
        Clean the selected keys if they are expired. 
        """
        for key in queryset:
            if key.has_expired():
                key.user.delete()
                key.delete()
    clean.short_description = 'Nettoyer les clés expirées'

    def revoke(self, request, queryset):
        """
        Delete the selected keys and users. 
        """
        for key in queryset:
            key.user.delete()
            key.delete()
    revoke.short_description = 'Annuler l\'inscription'

    def resend_activation_email(self, request, queryset):
        """
        Re-sends activation emails for the selected users.

        Note that this will *only* send activation emails for users
        who are eligible to activate; emails will not be sent to users
        whose activation keys have expired or who have already
        activated.
        """
        for profile in queryset:
            if not profile.has_expired():
                profile.send_activation_email()
    resend_activation_email.short_description = 'Renvoyer l\'e-mail d\'activation'


admin.site.register(Profile, ProfileAdmin)
admin.site.register(ActivationKey, ActivationKeyAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


