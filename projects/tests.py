from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date
from .models import Project, Criteria, Visit, VisitAssessment, VisitPhoto, ProjectInvitation


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
            realtor_name='John Doe',
            realtor_contact='john@test.com',
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