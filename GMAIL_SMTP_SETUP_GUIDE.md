# Gmail SMTP Email Verification Setup Guide

This guide will help you set up Gmail SMTP for email verification in your PSL Morph application. Gmail SMTP is free, reliable, works with Railway, and doesn't require domain verification.

## Prerequisites

- A Gmail account
- 2-Step Verification enabled on your Gmail account

## Step 1: Enable 2-Step Verification

1. Go to your [Google Account settings](https://myaccount.google.com/)
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click on "2-Step Verification"
4. Follow the setup process to enable 2-Step Verification

## Step 2: Generate App Password

1. After enabling 2-Step Verification, go back to the Security page
2. Under "Signing in to Google", click on "App passwords"
3. Select "Mail" as the app and "Other (Custom name)" as the device
4. Enter "PSL Morph" as the custom name
5. Click "Generate"
6. **Important**: Copy the 16-character app password immediately (it won't be shown again)

## Step 3: Update Environment Variables

Update your `.env` file with your Gmail credentials:

```env
# Gmail SMTP Configuration
GMAIL_EMAIL=your_actual_email@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password_here
```

**Example:**
```env
GMAIL_EMAIL=john.doe@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
```

## Step 4: Railway Deployment

For Railway deployment, you need to set these environment variables in your Railway project:

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add the following variables:
   - `GMAIL_EMAIL`: Your Gmail address
   - `GMAIL_APP_PASSWORD`: Your 16-character app password

## Step 5: Test the Configuration

Run the test script to verify your setup:

```bash
python test_gmail_smtp.py
```

## Security Best Practices

1. **Never commit your App Password to version control**
2. **Use environment variables for all sensitive data**
3. **Regenerate App Password if compromised**
4. **Keep your Gmail account secure with strong password**

## Troubleshooting

### Common Issues

1. **"Authentication failed" error**
   - Verify 2-Step Verification is enabled
   - Double-check your App Password (no spaces when entering)
   - Make sure you're using the App Password, not your regular Gmail password

2. **"Less secure app access" error**
   - This shouldn't happen with App Passwords, but if it does:
   - Make sure you're using an App Password, not your regular password
   - Try regenerating the App Password

3. **Connection timeout**
   - Check your internet connection
   - Verify Railway allows outbound SMTP connections (it does)

4. **"Username and Password not accepted" error**
   - Verify your Gmail address is correct
   - Regenerate your App Password and try again
   - Make sure there are no extra spaces in your credentials

### Testing Locally

To test locally before deploying:

1. Update your local `.env` file with Gmail credentials
2. Run the Flask app locally
3. Try registering a new account
4. Check if verification email is received

### Railway-Specific Notes

- Railway supports outbound SMTP connections
- No additional firewall configuration needed
- Gmail SMTP works reliably on Railway's infrastructure
- Make sure to set environment variables in Railway dashboard

## Email Templates

The system includes beautiful HTML email templates with:

- **Verification Email**: Professional welcome message with verification button
- **Welcome Email**: Congratulations message after successful verification
- **Responsive Design**: Works on all devices and email clients
- **Fallback Text**: Plain text version for compatibility

## Features

- ✅ **Free and Unlimited**: No cost for personal use
- ✅ **No Domain Verification**: Use any Gmail account
- ✅ **Railway Compatible**: Works perfectly with Railway deployment
- ✅ **Secure**: Uses App Passwords for authentication
- ✅ **Reliable**: Gmail's robust infrastructure
- ✅ **Professional**: Beautiful HTML email templates

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify your Gmail account settings
3. Test with a fresh App Password
4. Check Railway logs for detailed error messages

## Migration from EmailJS

If you're migrating from EmailJS:

1. The database schema remains the same
2. All authentication routes work unchanged
3. Only the email sending mechanism has changed
4. No frontend changes required

Your email verification system is now ready to use with Gmail SMTP!
