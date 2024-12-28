from django.urls import path
from thq_home.views import *

urlpatterns = [
    path('', home_view, name="home"),
    path('upgrade/', payment_index, name='upgrade_account'),
    path('payment/', payment, name='payment'),
    path('payment_return/', payment_return, name='payment_return'),

    path('writing/', writing_view, name='writing_index'),
    path('writing/evaluate/', writing_evaluate, name='writing_evaluate'),
]