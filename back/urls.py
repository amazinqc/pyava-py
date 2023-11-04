from django.urls import path

from . import views

app_name = 'back'

urlpatterns = [
    # 所有codes
    path("codes", views.codes, name="codes"),
    # 指定code类型的codes
    path("codes/<int:type_id>", views.codes, name="codes"),
    # 所有类型（大类）
    path("code/options", views.options, name="options"),
    # 指定类型的选项（二类/code类型）
    path("code/options/<int:option_id>", views.options, name="options"),
    # 所有服务器
    path("code/servers", views.servers, name="servers"),
    # 代码提示
    path("code/hints", views.hints, name="hints"),
    # 指定code读/写
    path('code/<int:id>', views.CodeView.as_view(), name='code'),
    # 调试草稿
    path('code/debug', views.debug, name='debug'),
]
