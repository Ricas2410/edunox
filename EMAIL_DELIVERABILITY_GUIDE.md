# Email Deliverability Guide for Edunox GH

## 🚨 Common Issues and Solutions

### Issue 1: Emails Going to Spam Folder

**Causes:**
- Missing email authentication (SPF, DKIM, DMARC)
- Poor sender reputation
- Generic/suspicious content
- Inconsistent sender information
- Development environment settings

**Solutions Implemented:**

#### 1. Enhanced Email Headers
- Added proper email headers for authentication
- Included Message-ID, Sender, Reply-To headers
- Added List-Unsubscribe header for compliance

#### 2. Improved Email Content
- Professional HTML templates with proper structure
- Consistent branding with logo
- Clear call-to-action buttons
- Proper text/HTML ratio

#### 3. Zoho-Specific Optimizations
- Increased timeout for Zoho SMTP (60 seconds)
- Validation of TLS settings
- Sender authentication checks

### Issue 2: Missing Logo in Emails

**Solution:**
- Updated email base template to include site logo
- Logo loads from SiteConfiguration settings
- Fallback handling for missing logos
- Proper image sizing for email clients

## 🔧 Technical Improvements Made

### 1. Enhanced Email Utilities (`core/email_utils.py`)

```python
# New functions added:
- get_email_headers()      # Anti-spam headers
- send_html_email()        # HTML email with templates
- Updated safe_send_mail() # Better error handling
```

### 2. Updated Email Templates

- `templates/emails/base.html` - Added logo support
- `templates/emails/email_verification.html` - Modernized design
- All templates now use consistent branding

### 3. Zoho SMTP Optimizations

- Automatic detection of Zoho servers
- Provider-specific timeout settings
- Authentication validation
- Port and encryption checks

## 📧 Email Authentication Setup

### For Production (Recommended)

1. **SPF Record** - Add to your DNS:
   ```
   v=spf1 include:zoho.com ~all
   ```

2. **DKIM** - Enable in Zoho Mail settings:
   - Go to Zoho Mail Admin Console
   - Navigate to Email Authentication
   - Enable DKIM for your domain

3. **DMARC** - Add to your DNS:
   ```
   v=DMARC1; p=quarantine; rua=mailto:dmarc@deigratiams.edu.gh
   ```

### For Development

- Use a dedicated development email address
- Consider using email testing services like Mailtrap
- Monitor spam scores with tools like Mail Tester

## 🎯 Best Practices for Email Deliverability

### 1. Sender Reputation
- Use consistent "From" email address
- Ensure "From" email matches authenticated domain
- Avoid frequent changes to sender information

### 2. Content Guidelines
- Maintain good text-to-image ratio
- Avoid spam trigger words
- Include clear unsubscribe options
- Use proper HTML structure

### 3. Technical Setup
- Enable TLS encryption
- Use proper SMTP authentication
- Monitor bounce rates
- Implement proper error handling

## 🧪 Testing Email Delivery

### 1. Test Email Configuration
```bash
# In Django shell
python manage.py shell

from core.email_utils import send_html_email
from django.contrib.auth.models import User

user = User.objects.first()
result = send_html_email(
    subject='Test Email',
    template_name='welcome',
    context={'user': user},
    recipient_list=['your-email@example.com']
)
print(f"Email sent: {result}")
```

### 2. Check Spam Score
- Use tools like Mail Tester (mail-tester.com)
- Send test emails to different providers
- Monitor delivery rates

### 3. Monitor Email Logs
- Check Django logs for email errors
- Monitor SMTP server logs
- Track bounce and complaint rates

## 🔍 Troubleshooting

### Emails Still Going to Spam
1. Check DNS records (SPF, DKIM, DMARC)
2. Verify sender reputation
3. Test email content with spam checkers
4. Consider using dedicated email service (SendGrid, Mailgun)

### Logo Not Displaying
1. Verify logo is uploaded in admin settings
2. Check image file permissions
3. Ensure proper URL generation
4. Test with different email clients

### SMTP Connection Issues
1. Verify Zoho credentials
2. Check firewall settings
3. Confirm TLS/SSL configuration
4. Test with different ports (587, 465)

## 📊 Monitoring and Maintenance

### Regular Checks
- Monitor email delivery rates
- Check spam folder placement
- Review bounce rates
- Update DNS records as needed

### Performance Optimization
- Use email queues for bulk sending
- Implement retry logic for failed sends
- Monitor SMTP connection health
- Regular cleanup of invalid email addresses

## 🚀 Next Steps

1. Set up proper DNS records for production
2. Consider dedicated email service for high volume
3. Implement email analytics and tracking
4. Regular monitoring and optimization
