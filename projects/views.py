from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
import json

from .models import Project, ProjectInvitation
from .forms import ProjectForm, ProjectInvitationForm


@login_required
def project_list(request):
    """Display list of user's projects."""
    # Get projects where user is owner or collaborator using Q objects
    from django.db.models import Q
    
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(collaborators=request.user)
    ).distinct()
    
    # Separate active and finished projects
    active_projects = user_projects.filter(status='active').order_by('-created_at')
    finished_projects = user_projects.filter(status='finished').order_by('-finished_at')
    
    context = {
        'active_projects': active_projects,
        'finished_projects': finished_projects,
        'has_projects': user_projects.exists(),
    }
    return render(request, 'projects/list.html', context)


@login_required
def project_create(request):
    """Create a new project."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create.html', {'form': form})


@login_required
def project_detail(request, pk):
    """Display project details and management interface."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    # Get pending invitations (only for project owner)
    pending_invitations = []
    if request.user == project.owner:
        pending_invitations = project.invitations.filter(accepted=False)
    
    context = {
        'project': project,
        'is_owner': request.user == project.owner,
        'pending_invitations': pending_invitations,
        'collaborators': project.collaborators.all(),
        'invitation_form': ProjectInvitationForm() if request.user == project.owner else None,
    }
    return render(request, 'projects/detail.html', context)


@login_required
def project_edit(request, pk):
    """Edit project details."""
    project = get_object_or_404(Project, pk=pk)
    
    # Only owner can edit project
    if request.user != project.owner:
        messages.error(request, "Only the project owner can edit project details.")
        return redirect('projects:detail', pk=project.pk)
    
    # Cannot edit finished projects
    if project.status == 'finished':
        messages.error(request, "Cannot edit finished projects.")
        return redirect('projects:detail', pk=project.pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/edit.html', {'form': form, 'project': project})


@login_required
@require_http_methods(["POST"])
def project_finish(request, pk):
    """Mark project as finished."""
    project = get_object_or_404(Project, pk=pk)
    
    # Only owner can finish project
    if request.user != project.owner:
        messages.error(request, "Only the project owner can finish projects.")
        return redirect('projects:detail', pk=project.pk)
    
    # Cannot finish already finished projects
    if project.status == 'finished':
        messages.warning(request, "Project is already finished.")
        return redirect('projects:detail', pk=project.pk)
    
    project.finish_project()
    messages.success(request, f'Project "{project.name}" has been finished and archived.')
    return redirect('projects:detail', pk=project.pk)


@login_required
@require_http_methods(["POST"])
def send_invitation(request, pk):
    """Send invitation to collaborate on project."""
    project = get_object_or_404(Project, pk=pk)
    
    # Only owner can send invitations
    if request.user != project.owner:
        messages.error(request, "Only the project owner can send invitations.")
        return redirect('projects:detail', pk=project.pk)
    
    # Cannot invite to finished projects
    if project.status == 'finished':
        messages.error(request, "Cannot invite collaborators to finished projects.")
        return redirect('projects:detail', pk=project.pk)
    
    form = ProjectInvitationForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        
        # Check if user is already a member
        try:
            user = User.objects.get(email=email)
            if project.is_member(user):
                messages.warning(request, f"{email} is already a member of this project.")
                return redirect('projects:detail', pk=project.pk)
        except User.DoesNotExist:
            pass
        
        # Check if invitation already exists
        existing_invitation = ProjectInvitation.objects.filter(
            project=project, 
            email=email, 
            accepted=False
        ).first()
        
        if existing_invitation:
            messages.warning(request, f"An invitation has already been sent to {email}.")
            return redirect('projects:detail', pk=project.pk)
        
        # Create invitation
        invitation = ProjectInvitation.objects.create(
            project=project,
            email=email,
            invited_by=request.user
        )
        
        # Send invitation email
        try:
            invitation_url = request.build_absolute_uri(
                reverse('projects:accept_invitation', kwargs={'token': invitation.token})
            )
            
            subject = f'Invitation to collaborate on "{project.name}"'
            message = f"""
Hello!

{request.user.email} has invited you to collaborate on the housing evaluation project "{project.name}".

Click the link below to accept the invitation:
{invitation_url}

If you don't have an account yet, you'll be able to create one when you accept the invitation.

Best regards,
The Checklist.casa Team
            """.strip()
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(request, f'Invitation sent to {email}!')
            
        except Exception as e:
            # If email fails, delete the invitation
            invitation.delete()
            messages.error(request, f'Failed to send invitation email. Please try again.')
    
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
    
    return redirect('projects:detail', pk=project.pk)


def accept_invitation(request, token):
    """Accept project invitation."""
    try:
        invitation = ProjectInvitation.objects.get(token=token, accepted=False)
    except ProjectInvitation.DoesNotExist:
        messages.error(request, "Invalid or expired invitation link.")
        return redirect('home')
    
    if request.user.is_authenticated:
        # User is logged in, check if email matches
        if request.user.email == invitation.email:
            # Accept invitation
            invitation.accept_invitation(request.user)
            messages.success(request, f'You have joined the project "{invitation.project.name}"!')
            return redirect('projects:detail', pk=invitation.project.pk)
        else:
            messages.error(request, 
                f"This invitation is for {invitation.email}, but you're logged in as {request.user.email}. "
                "Please log out and try again, or contact the project owner."
            )
            return redirect('projects:list')
    else:
        # User not logged in, redirect to login with next parameter
        login_url = reverse('account_login')
        invitation_url = reverse('projects:accept_invitation', kwargs={'token': token})
        return redirect(f'{login_url}?next={invitation_url}')


@login_required
@require_http_methods(["POST"])
def remove_collaborator(request, pk, user_id):
    """Remove collaborator from project."""
    project = get_object_or_404(Project, pk=pk)
    collaborator = get_object_or_404(User, pk=user_id)
    
    # Only owner can remove collaborators
    if request.user != project.owner:
        messages.error(request, "Only the project owner can remove collaborators.")
        return redirect('projects:detail', pk=project.pk)
    
    # Cannot modify finished projects
    if project.status == 'finished':
        messages.error(request, "Cannot modify finished projects.")
        return redirect('projects:detail', pk=project.pk)
    
    # Remove collaborator
    if project.collaborators.filter(pk=user_id).exists():
        project.collaborators.remove(collaborator)
        messages.success(request, f'{collaborator.email} has been removed from the project.')
    else:
        messages.warning(request, f'{collaborator.email} is not a collaborator on this project.')
    
    return redirect('projects:detail', pk=project.pk)


@login_required
@require_http_methods(["POST"])
def cancel_invitation(request, pk, invitation_id):
    """Cancel pending invitation."""
    project = get_object_or_404(Project, pk=pk)
    invitation = get_object_or_404(ProjectInvitation, pk=invitation_id, project=project)
    
    # Only owner can cancel invitations
    if request.user != project.owner:
        messages.error(request, "Only the project owner can cancel invitations.")
        return redirect('projects:detail', pk=project.pk)
    
    # Only cancel pending invitations
    if invitation.accepted:
        messages.warning(request, "Cannot cancel an already accepted invitation.")
        return redirect('projects:detail', pk=project.pk)
    
    email = invitation.email
    invitation.delete()
    messages.success(request, f'Invitation to {email} has been cancelled.')
    
    return redirect('projects:detail', pk=project.pk)