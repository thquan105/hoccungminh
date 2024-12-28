from django.urls import path
from thq_exams.views import *
import uuid

urlpatterns = [
    path('vocab/', vocab_search, name='vocab_search'),
    path('toggle-status/<uuid:deThi_id>/', toggle_status, name='toggle_status'),

    path('test/', test_index, name="test_index"),
    path('test/start/<uuid:deThi_id>/', test_start, name="test_start"),
    path('test/start/<uuid:deThi_id>/submit-test/', submit_test, name='submit_test'),

    path('practice/', practice_index, name="practice_index"),
    path('practice/create/', practice_create, name='practice_create'),
    path('practice/start/<uuid:deThi_id>/', practice_start, name='practice_start'),   
    path('practice/start/<uuid:deThi_id>/submit-answers/', submit_answers, name='submitanswers'),  
    path('practice/delete/<uuid:deThi_id>/', delete_practice, name='delete_practice'),

    path('history/', history_view, name='history_view'),
    path('history/<uuid:ketQua_id>/', test_result, name='test_result'),
]