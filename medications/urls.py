from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('register/',views.register),
    path('login/',views.login),
    path('home/', views.home_page),
    path('logout/',views.logout),
    path('medications/',views.medication_list),
    path('medications/create/', views.create_medications),
    path('medications/add/',views.add_medications),
    path('medications/table/', views.medications_table, name="medications_table"),
    path('medications/delete/<int:id>/', views.delete_medication),
    path('medications/<int:id>/edit/', views.edit_page),
    path('medications/<int:id>/update/',views.edit_medications),
]
