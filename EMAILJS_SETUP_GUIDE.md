# EmailJS Setup Guide for PSL Morph Email Verification

EmailJS is a free email service that works perfectly with Railway and doesn't require server-side SMTP configuration or domain verification. This guide will walk you through setting up EmailJS for email verification in your PSL Morph application.

## Why EmailJS?

- ✅ **Free**: 200 emails/month on free plan
- ✅ **No Domain Required**: Works with any email address
- ✅ **Railway Compatible**: No server-side SMTP configuration needed
- ✅ **Easy Setup**: Quick configuration through web interface
- ✅ **Reliable**: Handles email delivery through their infrastructure

## Step 1: Create EmailJS Account

1. Go to [https://emailjs.com](https://emailjs.com)
2. Click "Sign Up" and create a free account
3. Verify your email address

## Step 2: Add Email Service

1. In your EmailJS dashboard, go to "Email Services"
2. Click "Add New Service"
3. Choose your email provider (Gmail, Outlook, etc.)
4. Follow the setup instructions for your provider
5. Note down the **Service ID** (e.g., `service_abc123`)

### For Gmail:
- You'll need to enable 2-factor authentication
- Generate an App Password for EmailJS
- Use your Gmail address and the app password

## Step 3: Create Email Templates

You need to create two email templates: one for verification emails and one for welcome emails.

### Template 1: Verification Email

1. Go to "Email Templates" in your EmailJS dashboard
2. Click "Create New Template"
3. Use this template:

**Template Name**: `verification_email`

**Subject**: `{{subject}}`

**Content**:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }
        .content {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }
        .verify-button {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }
        .verify-button:hover {
            background: #218838;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎭 {{app_name}}</h1>
        <p>Verify Your Email Address</p>
    </div>
    
    <div class="content">
        <h2>Welcome to {{app_name}}!</h2>
        
        <p>Hello {{to_name}},</p>
        
        <p>Thank you for registering with {{app_name}}. To complete your registration and start using our face morphing services, please verify your email address.</p>
        
        <div style="text-align: center;">
            <a href="{{verification_url}}" class="verify-button">Verify Email Address</a>
        </div>
        
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px;">
            {{verification_url}}
        </p>
        
        <div class="warning">
            <strong>⚠️ Important:</strong> This verification link will expire in 24 hours. If you didn't create an account with {{app_name}}, please ignore this email.
        </div>
        
        <p>Once verified, you'll be able to:</p>
        <ul>
            <li>✨ Transform your photos with AI-powered face morphing</li>
            <li>🎯 Access premium morphing presets (HTN, Chadlite, Chad)</li>
            <li>💎 Get 5 free credits to start your journey</li>
            <li>📊 Request professional facial evaluations</li>
        </ul>
        
        <p>If you have any questions, feel free to contact our support team.</p>
        
        <p>Best regards,<br>
        The {{app_name}} Team</p>
    </div>
    
    <div class="footer">
        <p>This email was sent to {{to_email}}</p>
        <p>{{app_name}} - AI-Powered Face Transformation</p>
    </div>
</body>
</html>
```

4. Save the template and note down the **Template ID** (e.g., `template_xyz789`)

### Template 2: Welcome Email

1. Create another template for welcome emails
2. Use this template:

**Template Name**: `welcome_email`

**Subject**: `{{subject}}`

**Content**:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to PSL Morph</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }
        .content {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }
        .cta-button {
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }
        .cta-button:hover {
            background: #0056b3;
        }
        .feature-box {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Welcome to {{app_name}}!</h1>
        <p>Your account is now verified and ready to use</p>
    </div>
    
    <div class="content">
        <h2>Congratulations! 🎊</h2>
        
        <p>Hello {{to_name}},</p>
        
        <p>Your email has been successfully verified and your {{app_name}} account is now active. You're ready to start your face transformation journey!</p>
        
        <div style="text-align: center;">
            <a href="{{dashboard_url}}" class="cta-button">Start Morphing Now</a>
        </div>
        
        <h3>What's included with your account:</h3>
        
        <div class="feature-box">
            <h4>💎 5 Free Credits</h4>
            <p>Start exploring our AI-powered face morphing technology with 5 complimentary credits.</p>
        </div>
        
        <div class="feature-box">
            <h4>🎯 Premium Morphing Presets</h4>
            <p>Access to HTN, Chadlite, and Chad transformation presets for different enhancement levels.</p>
        </div>
        
        <div class="feature-box">
            <h4>📊 Professional Evaluations</h4>
            <p>Request detailed facial evaluations from our expert team.</p>
        </div>
        
        <div class="feature-box">
            <h4>🔄 Daily Free Generation</h4>
            <p>Get one free generation every day, even after using your initial credits.</p>
        </div>
        
        <p>Ready to get started? Visit your dashboard and upload your first photo!</p>
        
        <p>If you have any questions or need help, don't hesitate to reach out to our support team.</p>
        
        <p>Best regards,<br>
        The {{app_name}} Team</p>
    </div>
    
    <div class="footer">
        <p>This email was sent to {{to_email}}</p>
        <p>{{app_name}} - AI-Powered Face Transformation</p>
    </div>
</body>
</html>
```

3. Save the template and note down the **Template ID** (e.g., `template_welcome123`)

## Step 4: Get API Keys

1. Go to "Account" in your EmailJS dashboard
2. Find your **Public Key** (e.g., `user_abc123def456`)
3. Go to "Access Token" and create a **Private Key** (e.g., `accessToken_xyz789`)

## Step 5: Update Environment Variables

Update your `.env` file with the EmailJS credentials:

```env
# EmailJS Configuration
EMAILJS_SERVICE_ID=service_abc123
EMAILJS_TEMPLATE_ID=template_xyz789
EMAILJS_WELCOME_TEMPLATE_ID=template_welcome123
EMAILJS_PUBLIC_KEY=user_abc123def456
EMAILJS_PRIVATE_KEY=accessToken_xyz789
```

## Step 6: Test the Setup

1. Deploy your application to Railway
2. Try registering a new user
3. Check if the verification email is received
4. Verify the email and check if the welcome email is sent

## Template Variables

The following variables are automatically populated by the application:

### Verification Email:
- `{{to_email}}` - Recipient's email address
- `{{to_name}}` - Recipient's name (extracted from email)
- `{{subject}}` - Email subject
- `{{verification_url}}` - Verification link
- `{{app_name}}` - Application name (PSL Morph)

### Welcome Email:
- `{{to_email}}` - Recipient's email address
- `{{to_name}}` - Recipient's name (extracted from email)
- `{{subject}}` - Email subject
- `{{dashboard_url}}` - Link to dashboard
- `{{app_name}}` - Application name (PSL Morph)

## Troubleshooting

### Common Issues:

1. **Emails not sending**
   - Check if all environment variables are set correctly
   - Verify your EmailJS service is active
   - Check the EmailJS dashboard for error logs

2. **Template not found**
   - Ensure template IDs match exactly
   - Check if templates are published/active

3. **Rate limiting**
   - Free plan allows 200 emails/month
   - Consider upgrading if you need more

4. **Email in spam folder**
   - This is normal for new services
   - Users should check spam folder
   - Consider upgrading to a paid plan for better deliverability

## Upgrading EmailJS

If you need more than 200 emails/month:
- Personal plan: $15/month for 1,000 emails
- Team plan: $50/month for 5,000 emails

## Security Notes

- Keep your private key secure
- Don't expose API keys in client-side code
- The current implementation uses server-side API calls for security

## Support

- EmailJS Documentation: https://www.emailjs.com/docs/
- EmailJS Support: https://www.emailjs.com/support/

Your email verification system is now set up with EmailJS and ready for production use on Railway!
