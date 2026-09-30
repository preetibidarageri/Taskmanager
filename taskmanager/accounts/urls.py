from django.urls import path
from . import views
from accounts.admin import admin_site


urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.tasks, name='tasks'),
    path('add-task/', views.add_task, name='add_task'),
    path('update-task/<int:id>/', views.update_task, name='update_task'),
    path('delete-task/<int:id>/', views.delete_task, name='delete_task'),
    path('move-task/<int:id>/<str:status>/', views.move_task, name='move_task'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<int:id>/', views.reset_password, name='reset_password'),
    path( 'update-profile-pic/', views.update_profile_pic, name='update_profile_pic' ),
    path('profile/', views.profile, name='profile'),
    path('pdf-workspace/',
    views.pdf_workspace,
    name='pdf_workspace'
    ),
    path(
    'delete-pdf/<int:pdf_id>/',
    views.delete_pdf,
    name='delete_pdf'
    ),

    path(
    'save-progress/',
    views.save_progress,
    name='save_progress'
    ),
    path('calendar/', views.calendar_view, name='calendar'),
    path('reports/', views.reports, name='reports'),
   
]
