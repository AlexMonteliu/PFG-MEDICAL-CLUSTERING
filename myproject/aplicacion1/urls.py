from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello, name='hello'),
    path('predict_cluster/', views.predict_cluster, name='predict_cluster'),
]
