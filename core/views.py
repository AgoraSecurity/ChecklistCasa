from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from projects.models import Project


def home_view(request):
    """
    Smart home page that shows different content based on user state:
    - Not authenticated: Landing page with sign up/login
    - Authenticated but no projects: Create project prompt
    - Authenticated with projects but no active project: Project selection
    - Authenticated with active project: Log new visit prompt
    """
    if not request.user.is_authenticated:
        # User not logged in - show landing page
        return render(request, 'home.html', {
            'user_state': 'anonymous',
            'primary_action': 'signup',
            'secondary_action': 'login'
        })
    
    # User is authenticated - check their project status
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(collaborators=request.user)
    ).distinct()
    
    active_projects = user_projects.filter(status='active')
    
    if not user_projects.exists():
        # User has no projects - prompt to create one
        return render(request, 'home.html', {
            'user_state': 'no_projects',
            'primary_action': 'create_project'
        })
    
    if not active_projects.exists():
        # User has projects but none are active - show project list
        finished_projects = user_projects.filter(status='finished')
        return render(request, 'home.html', {
            'user_state': 'no_active_projects',
            'finished_projects': finished_projects,
            'primary_action': 'create_project',
            'secondary_action': 'view_projects'
        })
    
    # User has active projects
    if active_projects.count() == 1:
        # Single active project - show visit logging prompt
        active_project = active_projects.first()
        recent_visits = active_project.visits.all()[:3]
        
        return render(request, 'home.html', {
            'user_state': 'single_active_project',
            'active_project': active_project,
            'recent_visits': recent_visits,
            'primary_action': 'log_visit',
            'secondary_action': 'view_project'
        })
    else:
        # Multiple active projects - show project selection
        return render(request, 'home.html', {
            'user_state': 'multiple_active_projects',
            'active_projects': active_projects,
            'primary_action': 'view_projects',
            'secondary_action': 'create_project'
        })