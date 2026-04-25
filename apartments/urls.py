from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_apartment, name='add_apartment'),
    path('join/', views.join_apartment, name='join_apartment'),
    path('leave/<int:apartment_id>/', views.leave_apartment, name='leave_apartment'),
    path('remove-ownership/<int:apartment_id>/', views.remove_ownership, name='remove_ownership'),
]