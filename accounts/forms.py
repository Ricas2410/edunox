from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from .models import UserProfile, UserDocument


class UserProfileForm(forms.ModelForm):
    """User profile form"""
    
    # Add user fields
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 
            'gender', 'address', 'city', 'region', 'education_level', 
            'school_name', 'graduation_year', 'bio', 'profile_picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-fill user fields if instance exists
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4 class="mb-3">Personal Information</h4>'),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('date_of_birth', css_class='form-group col-md-6 mb-3'),
                Column('gender', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            HTML('<h4 class="mb-3 mt-4">Address Information</h4>'),
            'address',
            Row(
                Column('city', css_class='form-group col-md-6 mb-3'),
                Column('region', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            HTML('<h4 class="mb-3 mt-4">Education Information</h4>'),
            Row(
                Column('education_level', css_class='form-group col-md-6 mb-3'),
                Column('graduation_year', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'school_name',
            'bio',
            HTML('<h4 class="mb-3 mt-4">Profile Picture</h4>'),
            'profile_picture',
            HTML('<div class="mt-4">'),
            Submit('submit', 'Update Profile', css_class='btn btn-primary btn-lg'),
            HTML('</div>')
        )
        
        # Add labels and help text
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        self.fields['phone_number'].label = 'Phone Number'
        self.fields['date_of_birth'].label = 'Date of Birth'
        self.fields['graduation_year'].label = 'Graduation Year'
        self.fields['school_name'].label = 'School/Institution Name'
        self.fields['bio'].help_text = 'Tell us about yourself and your educational goals'
    
    def save(self, commit=True):
        """Save both User and UserProfile"""
        profile = super().save(commit=False)
        
        # Update user fields
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile.save()
        
        return profile


class UserDocumentForm(forms.ModelForm):
    """User document upload form"""
    
    class Meta:
        model = UserDocument
        fields = ['document_type', 'title', 'document_file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('document_type', css_class='form-group col-md-6 mb-3'),
                Column('title', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'document_file',
            'description',
            HTML('<div class="mt-3">'),
            Submit('submit', 'Upload Document', css_class='btn btn-primary'),
            HTML('</div>')
        )
        
        # Add labels and help text
        self.fields['document_type'].label = 'Document Type'
        self.fields['title'].label = 'Document Title'
        self.fields['document_file'].label = 'Select File'
        self.fields['description'].label = 'Description (Optional)'
        self.fields['description'].required = False


class RegistrationForm(forms.ModelForm):
    """Simplified registration form - only essential information"""

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a strong password'
        }),
        help_text='Password must be at least 8 characters long.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    # Optional profile fields
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number (optional)'
        })
    )

    education_level = forms.ChoiceField(
        choices=[('', 'Select your education level (optional)')] + [
            ('SHS', 'Senior High School'),
            ('DIPLOMA', 'Diploma'),
            ('BACHELOR', 'Bachelor\'s Degree'),
            ('MASTER', 'Master\'s Degree'),
            ('PHD', 'PhD'),
            ('OTHER', 'Other'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Terms acceptance
    accept_terms = forms.BooleanField(
        required=True,
        label='I agree to the Terms of Service and Privacy Policy',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make first_name and last_name required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h4 class="mb-3 text-gray-900">Create Your Account</h4>'),
            HTML('<p class="text-gray-600 mb-4">Join EduBridge Ghana to access our educational services. Additional profile information can be completed later.</p>'),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'email',
            HTML('<h4 class="mb-3 mt-4 text-gray-900">Secure Your Account</h4>'),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            HTML('<div class="mt-4 mb-3">'),
            'accept_terms',
            HTML('</div>'),
            HTML('<div class="mt-4">'),
            Submit('submit', 'Create Account', css_class='btn btn-primary btn-lg w-100'),
            HTML('</div>'),
            HTML('<p class="text-sm text-gray-600 mt-3 text-center">You can complete your profile information after creating your account.</p>')
        )
        
        # Make fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Add labels
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        self.fields['phone_number'].label = 'Phone Number (Optional)'
        self.fields['education_level'].label = 'Current Education Level'
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if user with this email already exists (since we use email as username)
            if User.objects.filter(username=email).exists():
                raise forms.ValidationError("An account with this email address already exists.")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean_password1(self):
        """Validate password strength"""
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            if password1.isdigit():
                raise forms.ValidationError("Password cannot be entirely numeric.")
            if password1.lower() in ['password', '12345678', 'qwerty']:
                raise forms.ValidationError("Password is too common. Please choose a stronger password.")
        return password1

    def clean_password2(self):
        """Validate password confirmation"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")

        return password2
    
    def save(self, commit=True):
        """Save user and create profile with optional fields"""
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

            # Create profile with optional fields
            profile, created = UserProfile.objects.get_or_create(user=user)

            # Save optional profile fields if provided
            if self.cleaned_data.get('phone_number'):
                profile.phone_number = self.cleaned_data['phone_number']
            if self.cleaned_data.get('education_level'):
                profile.education_level = self.cleaned_data['education_level']

            profile.save()

        return user
