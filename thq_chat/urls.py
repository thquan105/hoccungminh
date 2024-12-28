from django.urls import path
from thq_chat.views import *
import uuid

urlpatterns = [
    path('', chat_index, name="chat_index"),
    path('<uuid:cuocTroChuyen_id>/', chat_view, name="chat"),
    path('<uuid:cuocTroChuyen_id>/response/', response, name='response'),
    path('delete-chat/<uuid:cuocTroChuyen_id>/', delete_chat, name='delete_chat'),
]