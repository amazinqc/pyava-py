from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'back'

urlpatterns = [
    path("code/tools", (views.tools), name="tools"),
    path("code/tips", (views.hints), name="hints"),
    path('code/<int:id>', views.CodeView.as_view(), name='code'),
    path('code/debug', views.debug, name='debug'),
]
