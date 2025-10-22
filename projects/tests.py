from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from datetime import date
from .models import Project, Criteria, Visit, VisitAssessment, VisitPhoto, ProjectInvitation, Realtor


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collab@example.com',
            password='testpass123'
        )

    def test_project_creation(self):
        project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.status, 'active')
        self.assertIsNotNone(project.created_at)
        self.assertIsNone(project.finished_at)

    def test_project_finish(self):
        project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        project.finish_project()
        self.assertEqual(project.status, 'finished')
        self.assertIsNotNone(project.finished_at)

    def test_project_membership(self):
        project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        project.collaborators.add(self.collaborator)
        
        self.assertTrue(project.is_member(self.user))
        self.assertTrue(project.is_member(self.collaborator))
        
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )
        self.assertFalse(project.is_member(other_user))


class CriteriaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )

    def test_criteria_creation(self):
        criteria = Criteria.objects.create(
            project=self.project,
            name='Test Criteria',
            type='numeric',
            weight=0.8,
            order=1
        )
        self.assertEqual(criteria.name, 'Test Criteria')
        self.assertEqual(criteria.type, 'numeric')
        self.assertEqual(criteria.weight, 0.8)
        self.assertEqual(criteria.order, 1)

    def test_criteria_unique_name_per_project(self):
        Criteria.objects.create(
            project=self.project,
            name='Duplicate Name',
            type='boolean'
        )
        
        with self.assertRaises(IntegrityError):
            Criteria.objects.create(
                project=self.project,
                name='Duplicate Name',
                type='text'
            )


class VisitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )

    def test_visit_creation(self):
        visit = Visit.objects.create(
            project=self.project,
            name='Test Property',
            address='123 Test St',
            visit_date=date.today(),
            notes='Test notes',
            created_by=self.user
        )
        self.assertEqual(visit.name, 'Test Property')
        self.assertEqual(visit.address, '123 Test St')
        self.assertEqual(visit.created_by, self.user)


class VisitAssessmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        self.visit = Visit.objects.create(
            project=self.project,
            name='Test Property',
            address='123 Test St',
            visit_date=date.today(),
            created_by=self.user
        )

    def test_boolean_assessment(self):
        criteria = Criteria.objects.create(
            project=self.project,
            name='Has Parking',
            type='boolean'
        )
        assessment = VisitAssessment.objects.create(
            visit=self.visit,
            criteria=criteria
        )
        assessment.set_value(True)
        assessment.save()
        
        self.assertTrue(assessment.get_value())
        self.assertTrue(assessment.value_boolean)

    def test_numeric_assessment(self):
        criteria = Criteria.objects.create(
            project=self.project,
            name='Price',
            type='numeric'
        )
        assessment = VisitAssessment.objects.create(
            visit=self.visit,
            criteria=criteria
        )
        assessment.set_value(2500.50)
        assessment.save()
        
        self.assertEqual(assessment.get_value(), 2500.50)
        self.assertEqual(assessment.value_numeric, 2500.50)

    def test_rating_assessment(self):
        criteria = Criteria.objects.create(
            project=self.project,
            name='Overall Rating',
            type='rating'
        )
        assessment = VisitAssessment.objects.create(
            visit=self.visit,
            criteria=criteria
        )
        assessment.set_value(4)
        assessment.save()
        
        self.assertEqual(assessment.get_value(), 4)
        self.assertEqual(assessment.value_rating, 4)

    def test_text_assessment(self):
        criteria = Criteria.objects.create(
            project=self.project,
            name='Notes',
            type='text'
        )
        assessment = VisitAssessment.objects.create(
            visit=self.visit,
            criteria=criteria
        )
        assessment.set_value('Great location')
        assessment.save()
        
        self.assertEqual(assessment.get_value(), 'Great location')
        self.assertEqual(assessment.value_text, 'Great location')

    def test_unique_assessment_per_visit_criteria(self):
        criteria = Criteria.objects.create(
            project=self.project,
            name='Test Criteria',
            type='boolean'
        )
        
        VisitAssessment.objects.create(
            visit=self.visit,
            criteria=criteria
        )
        
        with self.assertRaises(IntegrityError):
            VisitAssessment.objects.create(
                visit=self.visit,
                criteria=criteria
            )


class ProjectInvitationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collab@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )

    def test_invitation_creation(self):
        invitation = ProjectInvitation.objects.create(
            project=self.project,
            email='invite@example.com',
            invited_by=self.user
        )
        self.assertEqual(invitation.email, 'invite@example.com')
        self.assertEqual(invitation.invited_by, self.user)
        self.assertFalse(invitation.accepted)
        self.assertIsNotNone(invitation.token)

    def test_invitation_acceptance(self):
        invitation = ProjectInvitation.objects.create(
            project=self.project,
            email=self.collaborator.email,
            invited_by=self.user
        )
        
        result = invitation.accept_invitation(self.collaborator)
        self.assertTrue(result)
        self.assertTrue(invitation.accepted)
        self.assertIsNotNone(invitation.accepted_at)
        self.assertTrue(self.project.collaborators.filter(id=self.collaborator.id).exists())

    def test_duplicate_invitation_prevention(self):
        ProjectInvitation.objects.create(
            project=self.project,
            email='duplicate@example.com',
            invited_by=self.user
        )
        
        with self.assertRaises(IntegrityError):
            ProjectInvitation.objects.create(
                project=self.project,
                email='duplicate@example.com',
                invited_by=self.user
            )


class ProjectManagementViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collab@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        self.project.collaborators.add(self.collaborator)

    def test_project_list_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_list_view_unauthenticated(self):
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_project_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/projects/create/', {
            'name': 'New Test Project'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Project.objects.filter(name='New Test Project').exists())

    def test_project_detail_view_owner(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/projects/{self.project.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_detail_view_collaborator(self):
        self.client.login(username='collaborator', password='testpass123')
        response = self.client.get(f'/projects/{self.project.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_detail_view_unauthorized(self):
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(f'/projects/{self.project.pk}/')
        self.assertEqual(response.status_code, 302)  # Redirect with error

    def test_project_edit_view_owner(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/edit/', {
            'name': 'Updated Project Name'
        })
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project Name')

    def test_project_edit_view_collaborator_denied(self):
        self.client.login(username='collaborator', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/edit/', {
            'name': 'Should Not Update'
        })
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Test Project')  # Should not change

    def test_project_finish_owner(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/finish/')
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'finished')
        self.assertIsNotNone(self.project.finished_at)

    def test_project_finish_collaborator_denied(self):
        self.client.login(username='collaborator', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/finish/')
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'active')  # Should not change


class ProjectCollaborationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collab@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )

    def test_send_invitation_owner(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/invite/', {
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProjectInvitation.objects.filter(
            project=self.project,
            email='newuser@example.com'
        ).exists())

    def test_send_invitation_collaborator_denied(self):
        self.project.collaborators.add(self.collaborator)
        self.client.login(username='collaborator', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/invite/', {
            'email': 'newuser@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ProjectInvitation.objects.filter(
            project=self.project,
            email='newuser@example.com'
        ).exists())

    def test_accept_invitation_authenticated(self):
        invitation = ProjectInvitation.objects.create(
            project=self.project,
            email=self.collaborator.email,
            invited_by=self.user
        )
        self.client.login(username='collaborator', password='testpass123')
        response = self.client.get(f'/projects/invitation/{invitation.token}/')
        self.assertEqual(response.status_code, 302)
        invitation.refresh_from_db()
        self.assertTrue(invitation.accepted)
        self.assertTrue(self.project.collaborators.filter(id=self.collaborator.id).exists())

    def test_accept_invitation_unauthenticated(self):
        invitation = ProjectInvitation.objects.create(
            project=self.project,
            email='newuser@example.com',
            invited_by=self.user
        )
        response = self.client.get(f'/projects/invitation/{invitation.token}/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_remove_collaborator_owner(self):
        self.project.collaborators.add(self.collaborator)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/remove/{self.collaborator.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.project.collaborators.filter(id=self.collaborator.id).exists())

    def test_cancel_invitation_owner(self):
        invitation = ProjectInvitation.objects.create(
            project=self.project,
            email='cancel@example.com',
            invited_by=self.user
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/cancel-invitation/{invitation.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ProjectInvitation.objects.filter(pk=invitation.pk).exists())


class ProjectFormTest(TestCase):
    def test_valid_project_form(self):
        from projects.forms import ProjectForm
        form_data = {'name': 'Valid Project Name'}
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_project_form_short_name(self):
        from projects.forms import ProjectForm
        form_data = {'name': 'AB'}  # Too short
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_valid_invitation_form(self):
        from projects.forms import ProjectInvitationForm
        form_data = {'email': 'test@example.com'}
        form = ProjectInvitationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_invitation_form(self):
        from projects.forms import ProjectInvitationForm
        form_data = {'email': 'invalid-email'}
        form = ProjectInvitationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class CriteriaManagementViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collab@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        self.project.collaborators.add(self.collaborator)

    def test_criteria_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/projects/{self.project.pk}/criteria/')
        self.assertEqual(response.status_code, 200)

    def test_criteria_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/criteria/create/', {
            'name': 'Test Criteria',
            'type': 'numeric',
            'weight': 1.5,
            'order': 1
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Criteria.objects.filter(name='Test Criteria').exists())

    def test_add_default_criteria_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/criteria/add-defaults/', {
            'template': 'basic_housing'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.project.criteria.count() > 0)


class VisitManagementViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        # Add some criteria for testing
        self.criteria = Criteria.objects.create(
            project=self.project,
            name='Test Criteria',
            type='numeric',
            order=1
        )

    def test_visit_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/projects/{self.project.pk}/visits/')
        self.assertEqual(response.status_code, 200)

    def test_visit_create_step1(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/projects/{self.project.pk}/visits/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Step 1')

    def test_visit_create_step1_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(f'/projects/{self.project.pk}/visits/create/', {
            'name': 'Test Property',
            'address': '123 Test Street, Test City, TC 12345',
            'visit_date': date.today().isoformat(),
            'notes': 'Test notes'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('step=2', response.url)


class CriteriaFormTest(TestCase):
    def test_valid_criteria_form(self):
        from projects.forms import CriteriaForm
        form_data = {
            'name': 'Test Criteria',
            'type': 'numeric',
            'weight': 1.5,
            'order': 1
        }
        form = CriteriaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_criteria_form_short_name(self):
        from projects.forms import CriteriaForm
        form_data = {
            'name': 'X',  # Too short
            'type': 'numeric',
            'order': 1
        }
        form = CriteriaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class VisitFormTest(TestCase):
    def test_valid_visit_form(self):
        from projects.forms import VisitForm
        form_data = {
            'name': 'Test Property',
            'address': '123 Test Street, Test City, TC 12345',
            'visit_date': date.today(),
            'notes': 'Test notes'
        }
        form = VisitForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_visit_form_short_name(self):
        from projects.forms import VisitForm
        form_data = {
            'name': 'X',  # Too short
            'address': '123 Test Street, Test City, TC 12345',
            'visit_date': date.today()
        }
        form = VisitForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class VisitAssessmentFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.user
        )
        self.boolean_criteria = Criteria.objects.create(
            project=self.project,
            name='Has Parking',
            type='boolean',
            order=1
        )
        self.numeric_criteria = Criteria.objects.create(
            project=self.project,
            name='Monthly Rent',
            type='numeric',
            order=2
        )

    def test_assessment_form_creation(self):
        from projects.forms import VisitAssessmentForm
        form = VisitAssessmentForm(self.project)
        self.assertEqual(len(form.fields), 2)
        self.assertIn(f'criteria_{self.boolean_criteria.id}', form.fields)
        self.assertIn(f'criteria_{self.numeric_criteria.id}', form.fields)

    def test_assessment_form_save(self):
        from projects.forms import VisitAssessmentForm
        visit = Visit.objects.create(
            project=self.project,
            name='Test Property',
            address='123 Test St',
            visit_date=date.today(),
            created_by=self.user
        )
        
        form_data = {
            f'criteria_{self.boolean_criteria.id}': True,
            f'criteria_{self.numeric_criteria.id}': 1500.00,
        }
        
        form = VisitAssessmentForm(self.project, data=form_data)
        self.assertTrue(form.is_valid())
        
        assessments = form.save_assessments(visit)
        self.assertEqual(len(assessments), 2)
        
        # Verify assessments were saved correctly
        boolean_assessment = VisitAssessment.objects.get(visit=visit, criteria=self.boolean_criteria)
        self.assertTrue(boolean_assessment.get_value())
        
        numeric_assessment = VisitAssessment.objects.get(visit=visit, criteria=self.numeric_criteria)
        self.assertEqual(numeric_assessment.get_value(), 1500.00)

class ComparisonViewTest(TestCase):
    """Test comparison table and export functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='comparisonuser',
            email='comparison@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Housing Project',
            owner=self.user
        )
        
        # Create test criteria
        self.criteria1 = Criteria.objects.create(
            project=self.project,
            name='Price',
            type='numeric',
            weight=2.0,
            order=1
        )
        self.criteria2 = Criteria.objects.create(
            project=self.project,
            name='Location Rating',
            type='rating',
            weight=1.5,
            order=2
        )
        
        # Create test visits
        self.visit1 = Visit.objects.create(
            project=self.project,
            name='House A',
            address='123 Main St',
            visit_date='2024-01-15',
            created_by=self.user
        )
        self.visit2 = Visit.objects.create(
            project=self.project,
            name='House B',
            address='456 Oak Ave',
            visit_date='2024-01-20',
            created_by=self.user
        )
        
        # Create test assessments
        assessment1 = VisitAssessment.objects.create(visit=self.visit1, criteria=self.criteria1)
        assessment1.set_value(250000)
        assessment1.save()
        
        assessment2 = VisitAssessment.objects.create(visit=self.visit1, criteria=self.criteria2)
        assessment2.set_value(4)
        assessment2.save()
        
        assessment3 = VisitAssessment.objects.create(visit=self.visit2, criteria=self.criteria1)
        assessment3.set_value(300000)
        assessment3.save()
        
        assessment4 = VisitAssessment.objects.create(visit=self.visit2, criteria=self.criteria2)
        assessment4.set_value(3)
        assessment4.save()
        
        self.client.login(username='comparisonuser', password='testpass123')
    
    def test_comparison_table_view(self):
        """Test comparison table view."""
        url = reverse('projects:comparison_table', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Property Comparison')
        self.assertContains(response, 'House A')
        self.assertContains(response, 'House B')
        self.assertContains(response, 'Price')
        self.assertContains(response, 'Location Rating')
    
    def test_comparison_table_sorting(self):
        """Test comparison table sorting functionality."""
        url = reverse('projects:comparison_table', kwargs={'pk': self.project.pk})
        response = self.client.get(url, {'sort': self.criteria1.id, 'order': 'asc'})
        self.assertEqual(response.status_code, 200)
        # Should contain sorted data
        self.assertContains(response, 'House A')
        self.assertContains(response, 'House B')
    
    def test_comparison_table_filtering(self):
        """Test comparison table filtering functionality."""
        url = reverse('projects:comparison_table', kwargs={'pk': self.project.pk})
        response = self.client.get(url, {
            'filter_criterion': self.criteria1.id,
            'filter_value': '250000'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'House A')
    
    def test_csv_export(self):
        """Test CSV export functionality."""
        url = reverse('projects:export_csv', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        # Check CSV content
        content = response.content.decode('utf-8')
        self.assertIn('House A', content)
        self.assertIn('House B', content)
        self.assertIn('Price', content)
    

    
    def test_comparison_unauthorized_access(self):
        """Test unauthorized access to comparison table."""
        other_user = User.objects.create_user(
            username='otherusercomp',
            email='othercomp@example.com',
            password='testpass123'
        )
        self.client.login(username='otherusercomp', password='testpass123')
        
        url = reverse('projects:comparison_table', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to projects list
    
    def test_comparison_no_visits(self):
        """Test comparison table with no visits."""
        # Create empty project
        empty_project = Project.objects.create(
            name='Empty Project',
            owner=self.user
        )
        
        url = reverse('projects:comparison_table', kwargs={'pk': empty_project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to visit list
    
    def test_comparison_no_criteria(self):
        """Test comparison table with no criteria."""
        # Create project with visits but no criteria
        project_no_criteria = Project.objects.create(
            name='No Criteria Project',
            owner=self.user
        )
        Visit.objects.create(
            project=project_no_criteria,
            name='Test Visit',
            address='123 Test St',
            visit_date='2024-01-15',
            created_by=self.user
        )
        
        url = reverse('projects:comparison_table', kwargs={'pk': project_no_criteria.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to criteria list