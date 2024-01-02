from django.urls import path

from . import views
from .views import telegram_users, create_user

urlpatterns = [
    path('telegram_users/', telegram_users, name='telegram_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('create_user/', create_user, name='create_user'),
]
