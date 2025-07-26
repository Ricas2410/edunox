from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Field
from .models import ContactMessage, ContactAttachment


class ContactForm(forms.ModelForm):
    """Contact form with file attachments"""
    
    attachments = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx,.txt',
            'class': 'form-control'
        }),
        help_text="You can attach a file. Allowed formats: PDF, JPG, PNG, DOC, DOCX, TXT. Max 5MB per file."
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill user information if logged in
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email
            if hasattr(user, 'profile'):
                self.fields['phone'].initial = user.profile.phone_number
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-3'),
                Column('subject', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'message',
            HTML('<div class="mb-3">'),
            Field('attachments', css_class='form-control'),
            HTML('</div>'),
            HTML('<div class="mt-4">'),
            Submit('submit', 'Send Message', css_class='btn btn-primary btn-lg'),
            HTML('</div>')
        )
        
        # Add labels
        self.fields['name'].label = 'Full Name'
        self.fields['email'].label = 'Email Address'
        self.fields['phone'].label = 'Phone Number (Optional)'
        self.fields['subject'].label = 'Subject'
        self.fields['message'].label = 'Message'
        self.fields['attachments'].label = 'Attachments (Optional)'
    
    def clean_attachments(self):
        """Validate file attachments"""
        files = self.files.getlist('attachments')
        
        if len(files) > 5:
            raise forms.ValidationError("You can upload a maximum of 5 files.")
        
        for file in files:
            # Check file size (5MB limit)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(f"File '{file.name}' is too large. Maximum size is 5MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.txt']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(f"File '{file.name}' has an unsupported format.")
        
        return files
