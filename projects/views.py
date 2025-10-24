from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from .services import EmailService
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Max
from django.db import models
from django.utils import timezone
import json
import logging
import csv
import io

logger = logging.getLogger(__name__)

from .models import Project, ProjectInvitation, Criteria, Visit, VisitAssessment, VisitPhoto, Realtor
from .forms import (
    ProjectForm, ProjectInvitationForm, CriteriaForm, VisitForm, 
    VisitAssessmentForm, VisitPhotoForm, DefaultCriteriaForm, RealtorForm
)


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
        
        # Send invitation email via Mailgun
        try:
            invitation_url = request.build_absolute_uri(
                reverse('projects:accept_invitation', kwargs={'token': invitation.token})
            )
            
            # Use EmailService to send invitation via Mailgun
            email_service = EmailService()
            result = email_service.send_invitation_email(
                email=email,
                project_name=project.name,
                invitation_url=invitation_url,
                invited_by_email=request.user.email
            )
            
            if result['status'] == 'success':
                messages.success(request, f'Invitation sent to {email}!')
            else:
                # If email fails, delete the invitation
                invitation.delete()
                messages.error(request, f'Failed to send invitation email: {result["message"]}')
            
        except Exception as e:
            # If email fails, delete the invitation
            invitation.delete()
            messages.error(request, f'Failed to send invitation email. Please try again.')
            logger.error(f'Failed to send invitation email: {e}')
    
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


# Criteria Management Views

@login_required
def criteria_list(request, pk):
    """Display and manage project criteria."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    criteria = project.criteria.all()
    
    context = {
        'project': project,
        'criteria': criteria,
        'can_edit': project.status == 'active',
    }
    return render(request, 'projects/criteria_list.html', context)


@login_required
def criteria_create(request, pk):
    """Create new criteria for project."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access and project is active
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    if project.status != 'active':
        messages.error(request, "Cannot add criteria to finished projects.")
        return redirect('projects:criteria_list', pk=project.pk)
    
    if request.method == 'POST':
        form = CriteriaForm(request.POST)
        if form.is_valid():
            criteria = form.save(commit=False)
            criteria.project = project
            
            # Set order if not provided
            if not criteria.order:
                max_order = project.criteria.aggregate(
                    max_order=models.Max('order')
                )['max_order'] or 0
                criteria.order = max_order + 1
            
            try:
                criteria.save()
                messages.success(request, f'Criteria "{criteria.name}" created successfully!')
                return redirect('projects:criteria_list', pk=project.pk)
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    form.add_error('name', 'A criteria with this name already exists in this project.')
                else:
                    messages.error(request, 'An error occurred while saving the criteria.')
    else:
        # Set default order
        max_order = project.criteria.aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0
        form = CriteriaForm(initial={'order': max_order + 1})
    
    context = {
        'project': project,
        'form': form,
        'title': 'Add New Criteria'
    }
    return render(request, 'projects/criteria_form.html', context)


@login_required
def criteria_edit(request, pk, criteria_id):
    """Edit existing criteria."""
    project = get_object_or_404(Project, pk=pk)
    criteria = get_object_or_404(Criteria, pk=criteria_id, project=project)
    
    # Check if user has access and project is active
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    if project.status != 'active':
        messages.error(request, "Cannot edit criteria in finished projects.")
        return redirect('projects:criteria_list', pk=project.pk)
    
    if request.method == 'POST':
        form = CriteriaForm(request.POST, instance=criteria)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Criteria "{criteria.name}" updated successfully!')
                return redirect('projects:criteria_list', pk=project.pk)
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    form.add_error('name', 'A criteria with this name already exists in this project.')
                else:
                    messages.error(request, 'An error occurred while updating the criteria.')
    else:
        form = CriteriaForm(instance=criteria)
    
    context = {
        'project': project,
        'criteria': criteria,
        'form': form,
        'title': f'Edit "{criteria.name}"'
    }
    return render(request, 'projects/criteria_form.html', context)


@login_required
@require_http_methods(["POST"])
def criteria_delete(request, pk, criteria_id):
    """Delete criteria."""
    project = get_object_or_404(Project, pk=pk)
    criteria = get_object_or_404(Criteria, pk=criteria_id, project=project)
    
    # Check if user has access and project is active
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    if project.status != 'active':
        messages.error(request, "Cannot delete criteria from finished projects.")
        return redirect('projects:criteria_list', pk=project.pk)
    
    criteria_name = criteria.name
    criteria.delete()
    messages.success(request, f'Criteria "{criteria_name}" deleted successfully!')
    
    return redirect('projects:criteria_list', pk=project.pk)


@login_required
def add_default_criteria(request, pk):
    """Add default criteria templates to project."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access and project is active
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    if project.status != 'active':
        messages.error(request, "Cannot add criteria to finished projects.")
        return redirect('projects:criteria_list', pk=project.pk)
    
    if request.method == 'POST':
        form = DefaultCriteriaForm(request.POST)
        if form.is_valid():
            template_criteria = form.get_template_criteria()
            added_count = 0
            
            for criteria_data in template_criteria:
                # Check if criteria with this name already exists
                if not project.criteria.filter(name=criteria_data['name']).exists():
                    Criteria.objects.create(
                        project=project,
                        **criteria_data
                    )
                    added_count += 1
            
            if added_count > 0:
                messages.success(request, f'Added {added_count} criteria from template!')
            else:
                messages.info(request, 'All criteria from this template already exist in your project.')
            
            return redirect('projects:criteria_list', pk=project.pk)
    else:
        form = DefaultCriteriaForm()
    
    context = {
        'project': project,
        'form': form,
    }
    return render(request, 'projects/add_default_criteria.html', context)


# Visit Management Views

@login_required
def visit_list(request, pk):
    """Display project visits."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    visits = project.visits.all()
    
    context = {
        'project': project,
        'visits': visits,
        'can_add': project.status == 'active',
    }
    return render(request, 'projects/visit_list.html', context)


@login_required
def visit_create(request, pk):
    """Create new visit with multi-step form."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access and project is active
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    if project.status != 'active':
        messages.error(request, "Cannot add visits to finished projects.")
        return redirect('projects:visit_list', pk=project.pk)
    
    # Check if project has criteria
    if not project.criteria.exists():
        messages.warning(request, 
            "Please add some evaluation criteria before logging visits. "
            "You can use default templates or create custom criteria."
        )
        return redirect('projects:criteria_list', pk=project.pk)
    
    step = request.GET.get('step', '1')
    
    if request.method == 'POST':
        logger.info(f"Visit creation POST request - Step: {step}, User: {request.user.id}, Project: {project.id}")
        
        if step == '1':
            # Step 1: Basic visit information
            visit_form = VisitForm(project=project, user=request.user, data=request.POST)
            
            # Handle "Add new realtor" selection
            if 'realtor_choice' in request.POST and request.POST['realtor_choice'] == 'add_new':
                # Redirect to realtor creation with return URL
                return redirect(f'/projects/{project.pk}/realtors/create/?next={request.path}')
            
            if visit_form.is_valid():
                logger.info(f"Step 1 form valid - storing data in session")
                # Store form data in session
                cleaned_data = visit_form.cleaned_data.copy()
                # Remove realtor_choice from session data as it's not a model field
                cleaned_data.pop('realtor_choice', None)
                request.session['visit_data'] = cleaned_data
                request.session['visit_data']['visit_date'] = cleaned_data['visit_date'].isoformat()
                # Handle realtor field
                if cleaned_data.get('realtor'):
                    request.session['visit_data']['realtor_id'] = cleaned_data['realtor'].id
                    request.session['visit_data'].pop('realtor', None)  # Remove non-serializable object
                return redirect(f"{request.path}?step=2")
            else:
                logger.warning(f"Step 1 form invalid - errors: {visit_form.errors}")
                # Form has errors, will be displayed in the template
        
        elif step == '2':
            # Step 2: Assessments
            assessment_form = VisitAssessmentForm(project, request.POST)
            if assessment_form.is_valid():
                logger.info(f"Step 2 form valid - creating visit")
                # Get visit data from session
                visit_data = request.session.get('visit_data')
                if not visit_data:
                    logger.error(f"Step 2 - no visit data in session")
                    messages.error(request, "Session expired. Please start over.")
                    return redirect('projects:visit_create', pk=project.pk)
                
                try:
                    # Create visit
                    from datetime import datetime
                    visit_data['visit_date'] = datetime.fromisoformat(visit_data['visit_date']).date()
                    
                    # Handle realtor
                    realtor = None
                    if 'realtor_id' in visit_data:
                        try:
                            realtor = Realtor.objects.get(id=visit_data.pop('realtor_id'))
                        except Realtor.DoesNotExist:
                            pass
                    
                    visit = Visit.objects.create(
                        project=project,
                        created_by=request.user,
                        realtor=realtor,
                        **visit_data
                    )
                    logger.info(f"Visit created with ID: {visit.id}")
                    
                    # Save assessments
                    assessments = assessment_form.save_assessments(visit)
                    logger.info(f"Saved {len(assessments)} assessments")
                    
                    # Store visit ID for photo upload
                    request.session['visit_id'] = visit.id
                    
                    # Clear visit data from session
                    if 'visit_data' in request.session:
                        del request.session['visit_data']
                    
                    return redirect(f"{request.path}?step=3")
                    
                except Exception as e:
                    logger.error(f"Error creating visit: {str(e)}")
                    messages.error(request, f"Error creating visit: {str(e)}")
                    return redirect('projects:visit_create', pk=project.pk)
            else:
                logger.warning(f"Step 2 form invalid - errors: {assessment_form.errors}")
                # Form has errors, will be displayed in the template
        
        elif step == '3':
            # Step 3: Photo upload
            visit_id = request.session.get('visit_id')
            if not visit_id:
                messages.error(request, "Session expired. Please start over.")
                return redirect('projects:visit_create', pk=project.pk)
            
            visit = get_object_or_404(Visit, pk=visit_id, project=project)
            
            # Handle photo uploads
            photos_uploaded = 0
            for i in range(5):  # Max 5 photos
                photo_file = request.FILES.get(f'photo_{i}')
                caption = request.POST.get(f'caption_{i}', '')
                
                if photo_file:
                    # Validate photo
                    if photo_file.size > 5 * 1024 * 1024:  # 5MB limit
                        messages.warning(request, f"Photo {i+1} was too large and skipped (max 5MB).")
                        continue
                    
                    if not photo_file.content_type.startswith('image/'):
                        messages.warning(request, f"Photo {i+1} was not a valid image and skipped.")
                        continue
                    
                    VisitPhoto.objects.create(
                        visit=visit,
                        image=photo_file,
                        caption=caption,
                        order=i
                    )
                    photos_uploaded += 1
            
            # Clear session
            if 'visit_id' in request.session:
                del request.session['visit_id']
            
            if photos_uploaded > 0:
                messages.success(request, f'Visit "{visit.name}" created successfully with {photos_uploaded} photos!')
            else:
                messages.success(request, f'Visit "{visit.name}" created successfully!')
            
            return redirect('projects:visit_detail', pk=project.pk, visit_id=visit.pk)
    
    # GET request or form with errors - show appropriate step
    if step == '1':
        # If we're here from a POST with errors, visit_form will already be defined
        if 'visit_form' not in locals():
            visit_form = VisitForm(project=project, user=request.user)
        
        context = {
            'project': project,
            'form': visit_form,
            'step': 1,
            'title': 'Step 1: Basic Information'
        }
        return render(request, 'projects/visit_create_step1.html', context)
    
    elif step == '2':
        # Check if we have visit data from step 1
        visit_data = request.session.get('visit_data')
        if not visit_data:
            logger.warning(f"Step 2 GET - no visit data in session")
            messages.error(request, "Please complete step 1 first.")
            return redirect('projects:visit_create', pk=project.pk)
        
        # If we're here from a POST with errors, assessment_form will already be defined
        if 'assessment_form' not in locals():
            assessment_form = VisitAssessmentForm(project)
        
        context = {
            'project': project,
            'form': assessment_form,
            'visit_data': visit_data,
            'step': 2,
            'title': 'Step 2: Property Assessment'
        }
        return render(request, 'projects/visit_create_step2.html', context)
    
    elif step == '3':
        # Check if we have visit ID
        visit_id = request.session.get('visit_id')
        if not visit_id:
            messages.error(request, "Please complete steps 1 and 2 first.")
            return redirect('projects:visit_create', pk=project.pk)
        
        visit = get_object_or_404(Visit, pk=visit_id, project=project)
        context = {
            'project': project,
            'visit': visit,
            'step': 3,
            'title': 'Step 3: Upload Photos (Optional)'
        }
        return render(request, 'projects/visit_create_step3.html', context)
    
    else:
        return redirect('projects:visit_create', pk=project.pk)


@login_required
def visit_detail(request, pk, visit_id):
    """Display visit details."""
    project = get_object_or_404(Project, pk=pk)
    visit = get_object_or_404(Visit, pk=visit_id, project=project)
    
    # Check if user has access to this project
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    assessments = visit.assessments.select_related('criteria').order_by('criteria__order')
    photos = visit.photos.all()
    
    context = {
        'project': project,
        'visit': visit,
        'assessments': assessments,
        'photos': photos,
        'can_edit': project.status == 'active',
    }
    return render(request, 'projects/visit_detail.html', context)


@login_required
def visit_edit(request, pk, visit_id):
    """Edit existing visit."""
    project = get_object_or_404(Project, pk=pk)
    visit = get_object_or_404(Visit, pk=visit_id, project=project)
    
    # Check if user has access and project is active
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    if project.status != 'active':
        messages.error(request, "Cannot edit visits in finished projects.")
        return redirect('projects:visit_detail', pk=project.pk, visit_id=visit.pk)
    
    if request.method == 'POST':
        visit_form = VisitForm(project=project, user=request.user, data=request.POST, instance=visit)
        assessment_form = VisitAssessmentForm(project, request.POST)
        
        if visit_form.is_valid() and assessment_form.is_valid():
            visit_form.save()
            
            # Update assessments
            assessment_form.save_assessments(visit)
            
            messages.success(request, f'Visit "{visit.name}" updated successfully!')
            return redirect('projects:visit_detail', pk=project.pk, visit_id=visit.pk)
    else:
        visit_form = VisitForm(project=project, user=request.user, instance=visit)
        
        # Pre-populate assessment form with existing data
        initial_data = {}
        for assessment in visit.assessments.all():
            field_name = f'criteria_{assessment.criteria.id}'
            initial_data[field_name] = assessment.get_value()
        
        assessment_form = VisitAssessmentForm(project, initial=initial_data)
    
    context = {
        'project': project,
        'visit': visit,
        'visit_form': visit_form,
        'assessment_form': assessment_form,
    }
    return render(request, 'projects/visit_edit.html', context)


@login_required
@require_http_methods(["POST"])
def visit_delete(request, pk, visit_id):
    """Delete visit."""
    project = get_object_or_404(Project, pk=pk)
    visit = get_object_or_404(Visit, pk=visit_id, project=project)
    
    # Check if user has access and project is active
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    if project.status != 'active':
        messages.error(request, "Cannot delete visits from finished projects.")
        return redirect('projects:visit_detail', pk=project.pk, visit_id=visit.pk)
    
    visit_name = visit.name
    visit.delete()
    messages.success(request, f'Visit "{visit_name}" deleted successfully!')
    
    return redirect('projects:visit_list', pk=project.pk)
# Realtor Management Views

@login_required
def realtor_create(request, pk):
    """Create new realtor for a project."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    next_url = request.GET.get('next', f'/projects/{project.pk}/visits/')
    
    if request.method == 'POST':
        form = RealtorForm(request.POST)
        if form.is_valid():
            realtor = form.save(commit=False)
            realtor.created_by = request.user
            
            try:
                realtor.save()
                messages.success(request, f'Realtor "{realtor.name}" created successfully!')
                return redirect(next_url)
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    form.add_error('name', 'A realtor with this name already exists.')
                else:
                    messages.error(request, 'An error occurred while saving the realtor.')
    else:
        form = RealtorForm()
    
    context = {
        'project': project,
        'form': form,
        'next_url': next_url,
        'title': 'Add New Realtor'
    }
    return render(request, 'projects/realtor_create.html', context)


# Realtor Management Views

@login_required
def realtor_list(request, pk):
    """Display project realtors."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    realtors = project.realtors.all()
    
    context = {
        'project': project,
        'realtors': realtors,
        'can_add': project.status == 'active',
    }
    return render(request, 'projects/realtor_list.html', context)


@login_required
def realtor_create(request, pk):
    """Create new realtor for project."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access and project is active
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    if project.status != 'active':
        messages.error(request, "Cannot add realtors to finished projects.")
        return redirect('projects:realtor_list', pk=project.pk)
    
    if request.method == 'POST':
        form = RealtorForm(request.POST)
        if form.is_valid():
            realtor = form.save(commit=False)
            realtor.project = project
            realtor.created_by = request.user
            
            try:
                realtor.save()
                messages.success(request, f'Realtor "{realtor.name}" added to project successfully!')
                return redirect('projects:realtor_list', pk=project.pk)
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    form.add_error('name', 'A realtor with this name already exists in this project.')
                else:
                    messages.error(request, 'An error occurred while saving the realtor.')
    else:
        form = RealtorForm()
    
    context = {
        'project': project,
        'form': form,
        'title': 'Add New Realtor'
    }
    return render(request, 'projects/realtor_form.html', context)


@login_required
def realtor_edit(request, pk, realtor_id):
    """Edit existing realtor."""
    project = get_object_or_404(Project, pk=pk)
    realtor = get_object_or_404(Realtor, pk=realtor_id, project=project)
    
    # Check if user has access and can edit
    if not realtor.can_be_edited_by(request.user):
        messages.error(request, "You don't have permission to edit this realtor.")
        return redirect('projects:realtor_list', pk=project.pk)
    
    if project.status != 'active':
        messages.error(request, "Cannot edit realtors in finished projects.")
        return redirect('projects:realtor_list', pk=project.pk)
    
    if request.method == 'POST':
        form = RealtorForm(request.POST, instance=realtor)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Realtor "{realtor.name}" updated successfully!')
                return redirect('projects:realtor_list', pk=project.pk)
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    form.add_error('name', 'A realtor with this name already exists in this project.')
                else:
                    messages.error(request, 'An error occurred while updating the realtor.')
    else:
        form = RealtorForm(instance=realtor)
    
    context = {
        'project': project,
        'realtor': realtor,
        'form': form,
        'title': f'Edit "{realtor.name}"'
    }
    return render(request, 'projects/realtor_form.html', context)


@login_required
@require_http_methods(["POST"])
def realtor_delete(request, pk, realtor_id):
    """Delete realtor."""
    project = get_object_or_404(Project, pk=pk)
    realtor = get_object_or_404(Realtor, pk=realtor_id, project=project)
    
    # Check if user has permission to delete
    if not realtor.can_be_deleted_by(request.user):
        messages.error(request, "You don't have permission to delete this realtor.")
        return redirect('projects:realtor_list', pk=project.pk)
    
    if project.status != 'active':
        messages.error(request, "Cannot delete realtors from finished projects.")
        return redirect('projects:realtor_list', pk=project.pk)
    
    realtor_name = realtor.name
    realtor.delete()
    messages.success(request, f'Realtor "{realtor_name}" deleted successfully!')
    
    return redirect('projects:realtor_list', pk=project.pk)

# Comparison and Export Views

@login_required
def comparison_table(request, pk):
    """Display comparison table with visits and criteria."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    # Get all visits and criteria
    visits = project.visits.prefetch_related('assessments__criteria').order_by('-visit_date')
    criteria = project.criteria.all().order_by('order')
    
    # Check if there's data to compare
    if not visits.exists():
        messages.info(request, "No visits to compare yet. Add some property visits first.")
        return redirect('projects:visit_list', pk=project.pk)
    
    if not criteria.exists():
        messages.info(request, "No criteria defined yet. Add evaluation criteria first.")
        return redirect('projects:criteria_list', pk=project.pk)
    
    # Build comparison data structure
    comparison_data = []
    criteria_stats = {}  # For color coding
    
    # Initialize criteria stats
    for criterion in criteria:
        criteria_stats[criterion.id] = {
            'values': [],
            'min_val': None,
            'max_val': None,
            'type': criterion.type
        }
    
    # Process each visit
    for visit in visits:
        visit_data = {
            'visit': visit,
            'assessments': {}
        }
        
        # Get assessments for this visit
        assessments = {a.criteria.id: a for a in visit.assessments.all()}
        
        for criterion in criteria:
            assessment = assessments.get(criterion.id)
            value = assessment.get_value() if assessment else None
            visit_data['assessments'][criterion.id] = {
                'assessment': assessment,
                'value': value,
                'display_value': format_assessment_value(value, criterion.type)
            }
            
            # Collect numeric values for statistics (for color coding)
            if value is not None and criterion.type in ['numeric', 'rating']:
                try:
                    numeric_value = float(value)
                    criteria_stats[criterion.id]['values'].append(numeric_value)
                except (ValueError, TypeError):
                    pass
        
        comparison_data.append(visit_data)
    
    # Calculate min/max for color coding
    for criterion_id, stats in criteria_stats.items():
        if stats['values']:
            stats['min_val'] = min(stats['values'])
            stats['max_val'] = max(stats['values'])
    
    # Handle sorting
    sort_by = request.GET.get('sort')
    sort_order = request.GET.get('order', 'desc')
    
    if sort_by:
        try:
            criterion_id = int(sort_by)
            if any(c.id == criterion_id for c in criteria):
                # Sort by this criterion
                def sort_key(item):
                    value = item['assessments'][criterion_id]['value']
                    if value is None:
                        return float('-inf') if sort_order == 'desc' else float('inf')
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return str(value) if value else ''
                
                comparison_data.sort(key=sort_key, reverse=(sort_order == 'desc'))
        except (ValueError, TypeError):
            pass
    
    context = {
        'project': project,
        'visits': visits,
        'criteria': criteria,
        'comparison_data': comparison_data,
        'criteria_stats': criteria_stats,
        'sort_by': sort_by,
        'sort_order': sort_order,
    }
    
    return render(request, 'projects/comparison_table.html', context)


def format_assessment_value(value, criteria_type):
    """Format assessment value for display."""
    if value is None:
        return '-'
    
    if criteria_type == 'boolean':
        return 'Yes' if value else 'No'
    elif criteria_type == 'rating':
        return f"{value}/5"
    elif criteria_type == 'numeric':
        try:
            # Format numbers nicely
            num_value = float(value)
            if num_value == int(num_value):
                return str(int(num_value))
            else:
                return f"{num_value:.2f}".rstrip('0').rstrip('.')
        except (ValueError, TypeError):
            return str(value)
    else:  # text
        return str(value)


@login_required
def export_csv(request, pk):
    """Export comparison data as CSV."""
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if not project.is_member(request.user):
        messages.error(request, "You don't have access to this project.")
        return redirect('projects:list')
    
    # Create HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_comparison.csv"'
    
    writer = csv.writer(response)
    
    # Get data
    visits = project.visits.prefetch_related('assessments__criteria').order_by('-visit_date')
    criteria = project.criteria.all().order_by('order')
    
    # Write header row
    header = ['Visit Name', 'Address', 'Visit Date', 'Realtor', 'Notes']
    header.extend([criterion.name for criterion in criteria])
    writer.writerow(header)
    
    # Write data rows
    for visit in visits:
        # Get assessments for this visit
        assessments = {a.criteria.id: a for a in visit.assessments.all()}
        
        row = [
            visit.name,
            visit.address,
            visit.visit_date.strftime('%Y-%m-%d'),
            str(visit.realtor) if visit.realtor else '',
            visit.notes
        ]
        
        # Add assessment values
        for criterion in criteria:
            assessment = assessments.get(criterion.id)
            value = assessment.get_value() if assessment else None
            formatted_value = format_assessment_value(value, criterion.type)
            row.append(formatted_value)
        
        writer.writerow(row)
    
    return response


