from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView
from .forms import ContactForm
from .models import ContactMessage, ContactAttachment
from core.models import SiteConfiguration


class ContactView(TemplateView):
    """Contact page view"""
    template_name = 'contact/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_config'] = SiteConfiguration.get_config()
        context['form'] = ContactForm(user=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            # Save the contact message
            contact_message = form.save(commit=False)
            if request.user.is_authenticated:
                contact_message.user = request.user
            contact_message.save()
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                ContactAttachment.objects.create(
                    contact_message=contact_message,
                    file=file
                )
            
            # Send notification email to admin
            try:
                site_config = SiteConfiguration.get_config()
                subject = f"New Contact Message: {contact_message.subject}"
                message = f"""
                New contact message received:
                
                Name: {contact_message.name}
                Email: {contact_message.email}
                Phone: {contact_message.phone}
                Subject: {contact_message.subject}
                
                Message:
                {contact_message.message}
                
                Attachments: {len(files)} file(s)
                
                View in admin: {request.build_absolute_uri('/admin/contact/contactmessage/')}
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [site_config.contact_email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Don't fail if email sending fails
            
            messages.success(
                request,
                'Thank you for your message! We have received your inquiry and will get back to you soon.'
            )
            return redirect('contact:contact')
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)
