from django import forms
from django.contrib.auth.models import User
from .models import Project


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""
    
    class Meta:
        model = Project
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter project name (e.g., "Q1 Move to San Jose")',
                'maxlength': '200'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 3:
                raise forms.ValidationError("Project name must be at least 3 characters long.")
        return name


class ProjectInvitationForm(forms.Form):
    """Form for inviting users to collaborate on a project."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Enter email address',
        }),
        help_text="Enter the email address of the person you want to invite."
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email