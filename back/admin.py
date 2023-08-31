from typing import Any, Optional
from django.contrib import admin
from django.db.models import F
from django.db.models.functions import Substr
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import Tool, ServerApi

# Register your models here.


class ToolAdmin(admin.ModelAdmin):
    readonly_fields = ['create_time', 'update_time']
    list_display = ['name', 'code', 'type']
    list_display_links = ['name']
    list_filter = ['update_time', 'type']
    search_fields = ('name',)
    search_help_text = '搜索功能'
    ordering = ['id']
    fieldsets = [
        ('详细数据', {"fields": ['name', 'cmd', 'type']}),
        ('时间记录', {"fields": readonly_fields})
    ]


admin.site.register(Tool, ToolAdmin)
admin.site.register(ServerApi)
