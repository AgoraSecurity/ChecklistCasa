from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def project_list(request):
    """Display list of user's projects."""
    return render(request, 'projects/list.html')