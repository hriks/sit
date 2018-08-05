# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from apis.models import User, Issue


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username", "first_name", "last_name", "modified", "created")
    search_fields = ("username", "first_name", "last_name")
    list_filter = ("created", "modified")


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("title", "assignee", "created_by", "status", "modified", "created")
    search_fields = ("status", "assignee__username", "created_by__username")
    list_filter = ("status", )
    raw_id_fields = ("created_by", "assignee")
    readonly_fields = ("status",)
