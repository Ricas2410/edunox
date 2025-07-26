# Gmail SMTP Setup Guide for Edunox GH

## 🚨 **Common Gmail Error: "Username and Password not accepted"**

This error occurs because Gmail has strict security requirements. Here's how to fix it:

## 📋 **Step-by-Step Gmail Setup**

### **Step 1: Enable 2-Factor Authentication**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click "2-Step Verification"
3. Follow the setup process to enable 2FA
4. **This is REQUIRED** - Gmail won't allow app passwords without 2FA

### **Step 2: Generate App Password**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click "2-Step Verification"
3. Scroll down and click "App passwords"
4. Select "Mail" as the app
5. Select "Other (Custom name)" as the device
6. Enter "Edunox GH" as the name
7. Click "Generate"
8. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
9. **Use this App Password, NOT your regular Gmail password**

### **Step 3: Configure Edunox GH Email Settings**
1. Go to Admin Panel → Site Configuration → Email tab
2. Use these **exact settings**:
   - **Email Backend**: `SMTP (Production)`
   - **SMTP Host**: `smtp.gmail.com`
   - **SMTP Port**: `587`
   - **SMTP Username**: Your full Gmail address (e.g., `yourname@gmail.com`)
   - **SMTP Password**: The 16-character App Password (no spaces)
   - **Use TLS**: ✅ **CHECKED** (Required for Gmail)
   - **Use SSL**: ❌ **UNCHECKED** (Don't use both TLS and SSL)
   - **Default From Email**: Your Gmail address

### **Step 4: Test Email Configuration**
1. Click "Save Changes" first
2. Then click "Test Email"
3. Enter your email address
4. Check your inbox (and spam folder)

## 🔧 **Troubleshooting Common Issues**

### **Error: "Username and Password not accepted"**
**Causes & Solutions:**
- ❌ Using regular password → ✅ Use App Password
- ❌ 2FA not enabled → ✅ Enable 2-Factor Authentication first
- ❌ Wrong username format → ✅ Use full email address
- ❌ Spaces in App Password → ✅ Remove all spaces from App Password

### **Error: "Less secure app access"**
- This is **deprecated** by Google
- **Solution**: Use App Passwords instead (requires 2FA)

### **Error: "Connection refused"**
**Check these settings:**
- ✅ Host: `smtp.gmail.com` (not `gmail.com`)
- ✅ Port: `587` (not 25 or 465)
- ✅ TLS enabled, SSL disabled

### **Error: "Authentication failed"**
- Double-check your App Password
- Make sure you're using the Gmail address that generated the App Password
- Try generating a new App Password

## 📧 **Alternative Email Providers**

If Gmail continues to cause issues, consider these alternatives:

### **Zoho Mail** (Recommended)
```
Host: smtp.zoho.com
Port: 587
TLS: Enabled
Username: your-email@zoho.com
Password: Your Zoho password (or App Password if 2FA enabled)
```

### **Outlook/Hotmail**
```
Host: smtp-mail.outlook.com
Port: 587
TLS: Enabled
Username: your-email@outlook.com
Password: Your Outlook password
```

### **SendGrid** (For high volume)
```
Host: smtp.sendgrid.net
Port: 587
TLS: Enabled
Username: apikey
Password: Your SendGrid API key
```

## 🧪 **Testing Your Configuration**

### **Quick Test Commands**
```python
# Test in Django shell
python manage.py shell

from django.core.mail import send_mail
from core.models import SiteConfiguration

config = SiteConfiguration.get_config()
config.apply_email_settings()

send_mail(
    'Test Email',
    'This is a test email from Edunox GH',
    'your-email@gmail.com',
    ['your-email@gmail.com'],
    fail_silently=False,
)
```

## 📱 **Mobile App Passwords**

If you're using Gmail on mobile devices, you might need separate App Passwords for:
- Edunox GH (this application)
- Your phone's email app
- Desktop email clients

Each application should have its own unique App Password.

## 🔒 **Security Best Practices**

1. **Never share your App Password**
2. **Use different App Passwords for different applications**
3. **Revoke unused App Passwords** in Google Account settings
4. **Monitor your account activity** regularly
5. **Use strong, unique passwords** for your Google account

## 📞 **Still Having Issues?**

If you're still experiencing problems:

1. **Check Google Account Activity**: Look for any security alerts
2. **Try a different browser**: Clear cache and cookies
3. **Wait 10-15 minutes**: Sometimes changes take time to propagate
4. **Generate a new App Password**: Delete the old one and create a new one
5. **Contact Google Support**: For account-specific issues

## ✅ **Success Checklist**

- [ ] 2-Factor Authentication enabled on Google Account
- [ ] App Password generated (16 characters)
- [ ] SMTP settings configured correctly in Edunox GH
- [ ] TLS enabled, SSL disabled
- [ ] Test email sent successfully
- [ ] Email received in inbox

Once you complete all these steps, your Gmail SMTP should work perfectly with Edunox GH!
