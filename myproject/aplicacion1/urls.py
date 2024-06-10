from django.urls import path
from .views import hello, predict_cluster, login_view, success_view

urlpatterns = [
    path('login/', login_view, name='login'),  # Asegúrate de que la ruta principal sea el login
    path('hello/', hello, name='hello'),
    path('predict_cluster/', predict_cluster, name='predict_cluster'),
    path('success/', success_view, name='success'),
]
