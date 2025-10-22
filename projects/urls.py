from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project management
    path('', views.project_list, name='list'),
    path('create/', views.project_create, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('<int:pk>/edit/', views.project_edit, name='edit'),
    path('<int:pk>/finish/', views.project_finish, name='finish'),
    path('<int:pk>/invite/', views.send_invitation, name='send_invitation'),
    path('<int:pk>/remove/<int:user_id>/', views.remove_collaborator, name='remove_collaborator'),
    path('<int:pk>/cancel-invitation/<int:invitation_id>/', views.cancel_invitation, name='cancel_invitation'),
    path('invitation/<uuid:token>/', views.accept_invitation, name='accept_invitation'),
    
    # Criteria management
    path('<int:pk>/criteria/', views.criteria_list, name='criteria_list'),
    path('<int:pk>/criteria/create/', views.criteria_create, name='criteria_create'),
    path('<int:pk>/criteria/<int:criteria_id>/edit/', views.criteria_edit, name='criteria_edit'),
    path('<int:pk>/criteria/<int:criteria_id>/delete/', views.criteria_delete, name='criteria_delete'),
    path('<int:pk>/criteria/add-defaults/', views.add_default_criteria, name='add_default_criteria'),
    
    # Visit management
    path('<int:pk>/visits/', views.visit_list, name='visit_list'),
    path('<int:pk>/visits/create/', views.visit_create, name='visit_create'),
    path('<int:pk>/visits/<int:visit_id>/', views.visit_detail, name='visit_detail'),
    path('<int:pk>/visits/<int:visit_id>/edit/', views.visit_edit, name='visit_edit'),
    path('<int:pk>/visits/<int:visit_id>/delete/', views.visit_delete, name='visit_delete'),
]