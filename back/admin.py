from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from .models import Tool, Server

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
        ('详细数据', {"fields": ['name', 'type', 'cmd']}),
        ('时间记录', {"classes": ['collapse'],"fields": readonly_fields})
    ]

    def __str__(self):
        return '测试功能'


class ServerAdmin(admin.ModelAdmin):

    def get_readonly_fields(self, request: HttpRequest, obj: Server = None) -> list[str] | tuple[Any, ...]:
        if obj is None:
            return []
        return ['sid']
    def __str__(self):
        return '服务器列表'

admin.site.register(Tool, ToolAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.site_header = "测试后台管理"
admin.site.site_url = 'http://127.0.0.1/api/'
admin.site.site_title = None