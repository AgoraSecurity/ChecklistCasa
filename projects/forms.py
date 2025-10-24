from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Criteria, Project, Realtor, Visit, VisitAssessment, VisitPhoto


class RangeInput(forms.TextInput):
    """Custom range input widget"""
    input_type = 'range'


class TelInput(forms.TextInput):
    """Custom telephone input widget"""
    input_type = 'tel'


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


class RealtorForm(forms.ModelForm):
    """Form for creating and editing realtors."""

    class Meta:
        model = Realtor
        fields = ['name', 'company', 'phone', 'email', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter realtor name',
                'maxlength': '100'
            }),
            'company': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Company name (optional)',
                'maxlength': '100'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '(555) 123-4567',
                'maxlength': '20'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'email@example.com'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Additional notes about this realtor (optional)',
                'rows': 3
            })
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Realtor name must be at least 2 characters long.")
        return name


class CriteriaForm(forms.ModelForm):
    """Form for creating and editing criteria."""

    class Meta:
        model = Criteria
        fields = ['name', 'type', 'weight', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter criteria name (e.g., "Distance to work")',
                'maxlength': '100'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'weight': RangeInput(attrs={
                'class': 'w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider',
                'min': '0.5',
                'max': '10',
                'step': '0.5',
                'data-show-value': 'true'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0'
            })
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Criteria name must be at least 2 characters long.")
        return name

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and (weight < 0.5 or weight > 10):
            raise forms.ValidationError("Weight must be between 0.5 and 10.")
        return weight


class VisitForm(forms.ModelForm):
    """Form for creating and editing visits."""

    # Add a custom field for realtor selection with "Add new" option
    realtor_choice = forms.ChoiceField(
        required=False,
        label="Realtor/Agent",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'id': 'realtor-select'
        })
    )

    class Meta:
        model = Visit
        fields = ['name', 'address', 'realtor', 'visit_date', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter property name or identifier',
                'maxlength': '200'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter full property address',
                'rows': 3
            }),
            'realtor': forms.Select(attrs={
                'class': 'hidden'  # Hide the actual realtor field, we'll use realtor_choice
            }),
            'visit_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Additional notes about the visit (optional)',
                'rows': 4
            })
        }

    def __init__(self, project=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up realtor choices based on project
        if project:
            realtors = project.realtors.all().order_by('name')
            choices = [('', 'No realtor selected')]
            choices.extend([(r.id, str(r)) for r in realtors])
            choices.append(('add_new', '+ Add new realtor'))

            self.fields['realtor_choice'].choices = choices

            # Set initial value if editing
            if self.instance and self.instance.realtor:
                self.fields['realtor_choice'].initial = self.instance.realtor.id

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError("Property name must be at least 2 characters long.")
        return name

    def clean_address(self):
        address = self.cleaned_data.get('address')
        return address

    def clean(self):
        cleaned_data = super().clean()
        realtor_choice = cleaned_data.get('realtor_choice')

        # Handle realtor selection
        if realtor_choice and realtor_choice != 'add_new' and realtor_choice != '':
            try:
                realtor = Realtor.objects.get(id=realtor_choice)
                cleaned_data['realtor'] = realtor
            except Realtor.DoesNotExist:
                pass

        return cleaned_data


class VisitAssessmentForm(forms.Form):
    """Dynamic form for visit assessments based on project criteria."""

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project

        # Create fields for each criteria
        criteria_count = 0
        for criteria in project.criteria.all():
            field_name = f'criteria_{criteria.id}'
            criteria_count += 1

            if criteria.type == 'boolean':
                self.fields[field_name] = forms.BooleanField(
                    label=criteria.name,
                    required=False,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
                    })
                )
            elif criteria.type == 'numeric':
                self.fields[field_name] = forms.DecimalField(
                    label=criteria.name,
                    required=False,
                    max_digits=10,
                    decimal_places=2,
                    widget=forms.NumberInput(attrs={
                        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                        'step': '0.01'
                    })
                )
            elif criteria.type == 'rating':
                self.fields[field_name] = forms.IntegerField(
                    label=criteria.name,
                    required=False,
                    min_value=1,
                    max_value=5,
                    widget=RangeInput(attrs={
                        'class': 'w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider',
                        'min': '1',
                        'max': '5',
                        'step': '1',
                        'data-criteria-type': 'rating',
                        'data-show-value': 'true'
                    }),
                    help_text="Scale from 1 (Poor) to 5 (Excellent)"
                )
            else:  # text
                self.fields[field_name] = forms.CharField(
                    label=criteria.name,
                    required=False,
                    widget=forms.Textarea(attrs={
                        'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                        'rows': 2
                    })
                )

        # Debug logging (only in development)
        import logging

        from django.conf import settings
        if settings.DEBUG:
            logger = logging.getLogger(__name__)
            logger.debug(f"VisitAssessmentForm initialized with {criteria_count} criteria, {len(self.fields)} fields")

    def save_assessments(self, visit):
        """Save assessment data for the visit."""
        import logging

        from django.conf import settings
        logger = logging.getLogger(__name__)

        assessments = []
        if settings.DEBUG:
            logger.debug(f"Saving assessments for visit {visit.id}")
            logger.debug(f"Cleaned data: {self.cleaned_data}")

        for criteria in self.project.criteria.all():
            field_name = f'criteria_{criteria.id}'
            value = self.cleaned_data.get(field_name)

            if settings.DEBUG:
                logger.debug(f"Processing {field_name} ({criteria.name}): {value}")

            if value is not None and value != '':
                # Get or create assessment
                assessment, created = VisitAssessment.objects.get_or_create(
                    visit=visit,
                    criteria=criteria
                )
                assessment.set_value(value)
                assessment.save()
                assessments.append(assessment)

                if settings.DEBUG:
                    logger.debug(f"Saved assessment for {criteria.name}: {assessment.get_value()}")

        logger.info(f"Saved {len(assessments)} assessments for visit {visit.id}")
        return assessments


class VisitPhotoForm(forms.ModelForm):
    """Form for uploading visit photos."""

    class Meta:
        model = VisitPhoto
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Photo caption (optional)',
                'maxlength': '200'
            })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large. Maximum size is 5MB.")

            # Check file type
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Please upload a valid image file.")

        return image


# Formset for multiple photo uploads
VisitPhotoFormSet = forms.modelformset_factory(
    VisitPhoto,
    form=VisitPhotoForm,
    extra=5,  # Allow up to 5 photos
    max_num=5,
    can_delete=True
)


class DefaultCriteriaForm(forms.Form):
    """Form for selecting default criteria templates."""

    TEMPLATE_CHOICES = [
        ('basic_housing', 'Basic Housing Evaluation'),
        ('rental_apartment', 'Rental Apartment'),
        ('home_purchase', 'Home Purchase'),
        ('student_housing', 'Student Housing'),
        ('family_home', 'Family Home'),
    ]

    template = forms.ChoiceField(
        choices=TEMPLATE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        help_text="Select a template to add common criteria for your project type."
    )

    def get_template_criteria(self):
        """Return criteria for the selected template."""
        template = self.cleaned_data.get('template')

        templates = {
            'basic_housing': [
                {'name': 'Monthly Rent/Price', 'type': 'numeric', 'weight': 2.0, 'order': 1},
                {'name': 'Distance to Work', 'type': 'numeric', 'weight': 1.5, 'order': 2},
                {'name': 'Public Transportation Access', 'type': 'rating', 'weight': 1.0, 'order': 3},
                {'name': 'Neighborhood Safety', 'type': 'rating', 'weight': 2.0, 'order': 4},
                {'name': 'Overall Condition', 'type': 'rating', 'weight': 1.5, 'order': 5},
                {'name': 'Parking Available', 'type': 'boolean', 'weight': 1.0, 'order': 6},
                {'name': 'Pet Friendly', 'type': 'boolean', 'weight': None, 'order': 7},
                {'name': 'Additional Notes', 'type': 'text', 'weight': None, 'order': 8},
            ],
            'rental_apartment': [
                {'name': 'Monthly Rent', 'type': 'numeric', 'weight': 2.0, 'order': 1},
                {'name': 'Security Deposit', 'type': 'numeric', 'weight': 1.0, 'order': 2},
                {'name': 'Square Footage', 'type': 'numeric', 'weight': 1.5, 'order': 3},
                {'name': 'Number of Bedrooms', 'type': 'numeric', 'weight': 1.5, 'order': 4},
                {'name': 'Number of Bathrooms', 'type': 'numeric', 'weight': 1.0, 'order': 5},
                {'name': 'Laundry in Unit', 'type': 'boolean', 'weight': 1.0, 'order': 6},
                {'name': 'Air Conditioning', 'type': 'boolean', 'weight': 1.0, 'order': 7},
                {'name': 'Balcony/Patio', 'type': 'boolean', 'weight': 0.5, 'order': 8},
                {'name': 'Gym/Amenities', 'type': 'rating', 'weight': 0.5, 'order': 9},
                {'name': 'Noise Level', 'type': 'rating', 'weight': 1.5, 'order': 10},
            ],
            'home_purchase': [
                {'name': 'Purchase Price', 'type': 'numeric', 'weight': 2.0, 'order': 1},
                {'name': 'Property Tax (Annual)', 'type': 'numeric', 'weight': 1.5, 'order': 2},
                {'name': 'HOA Fees (Monthly)', 'type': 'numeric', 'weight': 1.0, 'order': 3},
                {'name': 'Square Footage', 'type': 'numeric', 'weight': 1.5, 'order': 4},
                {'name': 'Lot Size', 'type': 'numeric', 'weight': 1.0, 'order': 5},
                {'name': 'Year Built', 'type': 'numeric', 'weight': 1.0, 'order': 6},
                {'name': 'School District Rating', 'type': 'rating', 'weight': 2.0, 'order': 7},
                {'name': 'Home Condition', 'type': 'rating', 'weight': 2.0, 'order': 8},
                {'name': 'Garage Spaces', 'type': 'numeric', 'weight': 0.5, 'order': 9},
                {'name': 'Needs Major Repairs', 'type': 'boolean', 'weight': 1.5, 'order': 10},
            ],
            'student_housing': [
                {'name': 'Monthly Rent', 'type': 'numeric', 'weight': 2.0, 'order': 1},
                {'name': 'Distance to Campus', 'type': 'numeric', 'weight': 2.0, 'order': 2},
                {'name': 'Internet Speed', 'type': 'rating', 'weight': 1.5, 'order': 3},
                {'name': 'Study Space Quality', 'type': 'rating', 'weight': 1.5, 'order': 4},
                {'name': 'Roommate Compatibility', 'type': 'rating', 'weight': 1.0, 'order': 5},
                {'name': 'Kitchen Facilities', 'type': 'rating', 'weight': 1.0, 'order': 6},
                {'name': 'Furnished', 'type': 'boolean', 'weight': 1.0, 'order': 7},
                {'name': 'Utilities Included', 'type': 'boolean', 'weight': 1.0, 'order': 8},
                {'name': 'Social Environment', 'type': 'rating', 'weight': 0.5, 'order': 9},
            ],
            'family_home': [
                {'name': 'Purchase/Rent Price', 'type': 'numeric', 'weight': 2.0, 'order': 1},
                {'name': 'Number of Bedrooms', 'type': 'numeric', 'weight': 2.0, 'order': 2},
                {'name': 'Number of Bathrooms', 'type': 'numeric', 'weight': 1.5, 'order': 3},
                {'name': 'School District Rating', 'type': 'rating', 'weight': 2.0, 'order': 4},
                {'name': 'Distance to Schools', 'type': 'numeric', 'weight': 1.5, 'order': 5},
                {'name': 'Yard/Outdoor Space', 'type': 'rating', 'weight': 1.5, 'order': 6},
                {'name': 'Neighborhood Safety', 'type': 'rating', 'weight': 2.0, 'order': 7},
                {'name': 'Playgrounds Nearby', 'type': 'boolean', 'weight': 1.0, 'order': 8},
                {'name': 'Family-Friendly Amenities', 'type': 'rating', 'weight': 1.0, 'order': 9},
                {'name': 'Storage Space', 'type': 'rating', 'weight': 1.0, 'order': 10},
            ],
        }

        return templates.get(template, [])
