from typing import Any

from django.contrib import admin
from django.http.request import HttpRequest

from .models import Server, Tool, TypeChoice

# Register your models here.


class TypeAdmin(admin.ModelAdmin):
    list_display = ['type', 'desc', 'option']
    list_display_links = ['type', 'desc']
    list_filter = ['option']
    ordering = ['type']

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return not (obj and obj.tool_set.exists())


class ToolAdmin(admin.ModelAdmin):
    readonly_fields = ['create_time', 'update_time']
    list_display = ['name', 'abbr', 'type']
    list_display_links = ['name', 'abbr']
    list_filter = ['update_time', 'type']
    search_fields = ('name',)
    search_help_text = '按功能搜索'
    ordering = ['id']
    fieldsets = [
        ('详细数据', {"fields": ['name', 'type', 'cmd']}),
        ('时间记录', {"classes": ['collapse'], "fields": readonly_fields})
    ]

    def abbr(self, tool: Tool) -> str:
        '''
        自定义后台显示字段，超长代码缩略显示
        '''
        return '\r\n'.join(f"{arg.get('desc') or arg.get('name')}: {arg.get('type', '')}={arg.get('default', '')}" for arg in tool.args())
    abbr.short_description = '运行参数需求'

    def __str__(self):
        return '测试功能'


class ServerAdmin(admin.ModelAdmin):

    fields = ['sid', 'name', 'host', 'port']

    def get_readonly_fields(self, _: HttpRequest, obj: Server = None) -> list[str] | tuple[Any, ...]:
        if obj is None:
            return []
        return ['sid']

    def __str__(self):
        return '服务器列表'


admin.site.register(TypeChoice, TypeAdmin)
admin.site.register(Tool, ToolAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.site_header = "测试后台管理"
admin.site.site_url = 'http://127.0.0.1/api/'
admin.site.site_title = None
