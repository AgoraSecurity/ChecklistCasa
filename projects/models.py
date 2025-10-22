import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Project(models.Model):
    """
    A project represents a housing search with criteria and visits.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('finished', 'Finished'),
    ]
    
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_projects'
    )
    collaborators = models.ManyToManyField(
        User, 
        related_name='collaborated_projects', 
        blank=True
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def finish_project(self):
        """Mark project as finished and set timestamp."""
        self.status = 'finished'
        self.finished_at = timezone.now()
        self.save()
    
    def is_member(self, user):
        """Check if user is owner or collaborator."""
        return user == self.owner or self.collaborators.filter(id=user.id).exists()


class Criteria(models.Model):
    """
    Evaluation criteria for a project with different data types.
    """
    TYPE_CHOICES = [
        ('boolean', 'Yes/No'),
        ('numeric', 'Number'),
        ('text', 'Text'),
        ('rating', 'Rating 1-5'),
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='criteria'
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    weight = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Optional weight for this criteria (0.01-9.99)"
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = 'Criteria'
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Visit(models.Model):
    """
    A visit to a specific property for evaluation.
    """
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='visits'
    )
    name = models.CharField(max_length=200, help_text="Property name or identifier")
    address = models.TextField()
    realtor_name = models.CharField(max_length=100, blank=True)
    realtor_contact = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Phone number or email"
    )
    visit_date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.visit_date}"


class VisitAssessment(models.Model):
    """
    Assessment of a visit against specific criteria with polymorphic value storage.
    """
    visit = models.ForeignKey(
        Visit, 
        on_delete=models.CASCADE, 
        related_name='assessments'
    )
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE)
    
    # Polymorphic value storage based on criteria type
    value_text = models.TextField(blank=True)
    value_numeric = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    value_boolean = models.BooleanField(null=True, blank=True)
    value_rating = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['visit', 'criteria']
        ordering = ['criteria__order']
    
    def __str__(self):
        return f"{self.visit.name} - {self.criteria.name}"
    
    def get_value(self):
        """Get the appropriate value based on criteria type."""
        if self.criteria.type == 'boolean':
            return self.value_boolean
        elif self.criteria.type == 'numeric':
            return self.value_numeric
        elif self.criteria.type == 'rating':
            return self.value_rating
        else:  # text
            return self.value_text
    
    def set_value(self, value):
        """Set the appropriate value based on criteria type."""
        # Clear all values first
        self.value_text = ''
        self.value_numeric = None
        self.value_boolean = None
        self.value_rating = None
        
        # Set the appropriate value
        if self.criteria.type == 'boolean':
            self.value_boolean = bool(value) if value is not None else None
        elif self.criteria.type == 'numeric':
            self.value_numeric = float(value) if value is not None else None
        elif self.criteria.type == 'rating':
            self.value_rating = int(value) if value is not None else None
        else:  # text
            self.value_text = str(value) if value is not None else ''


class VisitPhoto(models.Model):
    """
    Photos associated with a visit.
    """
    visit = models.ForeignKey(
        Visit, 
        on_delete=models.CASCADE, 
        related_name='photos'
    )
    image = models.ImageField(upload_to='visit_photos/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"{self.visit.name} - Photo {self.order + 1}"


class ProjectInvitation(models.Model):
    """
    Invitations to collaborate on a project.
    """
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='invitations'
    )
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['project', 'email']
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Accepted" if self.accepted else "Pending"
        return f"{self.project.name} - {self.email} ({status})"
    
    def accept_invitation(self, user):
        """Accept the invitation and add user as collaborator."""
        if not self.accepted:
            self.accepted = True
            self.accepted_at = timezone.now()
            self.save()
            self.project.collaborators.add(user)
            return True
        return False