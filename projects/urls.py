from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('create/', views.project_create, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('<int:pk>/edit/', views.project_edit, name='edit'),
    path('<int:pk>/finish/', views.project_finish, name='finish'),
    path('<int:pk>/invite/', views.send_invitation, name='send_invitation'),
    path('<int:pk>/remove/<int:user_id>/', views.remove_collaborator, name='remove_collaborator'),
    path('<int:pk>/cancel-invitation/<int:invitation_id>/', views.cancel_invitation, name='cancel_invitation'),
    path('invitation/<uuid:token>/', views.accept_invitation, name='accept_invitation'),
]