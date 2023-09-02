from django.urls import path

from . import views

app_name = 'back'

urlpatterns = [
    path("", views.index, name="index"),
    path("code/tools", views.tools, name="tools"),
    path("code/tips", views.tips, name="tips"),
    path('code/<int:id>/', views.code, name='code'),
    path('code/debug', views.debug, name='debug'),
]
