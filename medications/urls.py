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
    path('reminders/', views.reminder_page),
    path('reminders/create/', views.create_reminder),
    path('reminders/table/', views.reminders_table),
    path('reminders/<int:id>/edit/', views.edit_reminders_page),
    path('reminders/<int:id>/update/', views.update_reminders),
    path('reminders/<int:id>/delete/', views.delete_reminders),
    path('about/', views.about_page),
    path('contact/', views.contact_page),
    path('contact/create/', views.create_contact),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/upcoming-reminders/', views.get_upcoming_reminders, name='upcoming_reminders'),
    path('reminders/<int:id>/mark-done/', views.mark_reminder_done, name='mark_reminder_done'),
]
