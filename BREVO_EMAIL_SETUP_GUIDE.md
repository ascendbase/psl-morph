# Brevo (Sendinblue) Email Verification Setup Guide

This guide will help you set up Brevo for email verification in your PSL Morph application. Brevo is the perfect solution for your requirements:

- ✅ **Free and unlimited** - 300 emails/day free tier
- ✅ **Works with Railway** - Uses HTTPS API, no SMTP ports
- ✅ **No domain verification** required for basic sending
- ✅ **Easy setup** - Just need an API key
- ✅ **Reliable** infrastructure

## Step 1: Create Brevo Account

1. Go to [https://brevo.com](https://brevo.com)
2. Click "Sign up free"
3. Fill in your details and verify your email
4. Complete the account setup

## Step 2: Get Your API Key

1. After logging in, go to your Brevo dashboard
2. Click on your name in the top right corner
3. Select "SMTP & API"
4. Click on "API Keys" tab
5. Click "Generate a new API key"
6. Give it a name like "PSL Morph Email"
7. **Copy the API key immediately** (it won't be shown again)

## Step 3: Update Environment Variables

Update your `.env` file with your Brevo credentials:

```env
# Brevo (Sendinblue) API Configuration
BREVO_API_KEY=your_actual_api_key_here
BREVO_FROM_EMAIL=noreply@example.com
BREVO_FROM_NAME=PSL Morph
BASE_URL=https://psl-morph-production.up.railway.app
```

**Example:**
```env
BREVO_API_KEY=xkeysib-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6-AbCdEfGhIjKlMnOp
BREVO_FROM_EMAIL=noreply@pslmorph.com
BREVO_FROM_NAME=PSL Morph
```

## Step 4: Railway Deployment

For Railway deployment, set these environment variables:

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add these variables:
   - `BREVO_API_KEY`: Your Brevo API key
   - `BREVO_FROM_EMAIL`: Your sender email (can be any email)
   - `BREVO_FROM_NAME`: Your sender name (PSL Morph)

## Step 5: Test the Configuration

Run the test script to verify your setup:

```bash
python test_brevo_email.py
```

## Features

### Free Tier Limits
- **300 emails per day** - Perfect for getting started
- **Unlimited contacts**
- **Email templates**
- **Real-time statistics**

### Email Templates
The system includes:
- **Professional verification emails** with PSL Morph branding
- **Welcome emails** after successful verification
- **Mobile-responsive design**
- **Both HTML and plain text versions**

### Security Features
- **Secure API authentication**
- **24-hour token expiration**
- **HTTPS-only communication**
- **No sensitive data in logs**

## Troubleshooting

### Common Issues

1. **"Invalid API key" error**
   - Verify your API key is correct
   - Make sure there are no extra spaces
   - Regenerate the API key if needed

2. **"Sender not authorized" error**
   - This shouldn't happen with Brevo's free tier
   - Try using a different FROM_EMAIL address

3. **Emails not received**
   - Check spam folder
   - Verify the recipient email is correct
   - Check Brevo dashboard for delivery status

4. **Rate limit exceeded**
   - You've hit the 300 emails/day limit
   - Wait until the next day or upgrade your plan

### Testing Commands

```bash
# Test Brevo API connection
python test_brevo_email.py

# Check if imports work
python -c "from email_utils import send_verification_email; print('Import successful')"

# Test token generation
python -c "from email_utils import generate_verification_token; print(generate_verification_token())"
```

## Brevo Dashboard

After setting up, you can monitor your emails in the Brevo dashboard:

1. **Statistics** - See delivery rates, opens, clicks
2. **Logs** - View all sent emails and their status
3. **Templates** - Create reusable email templates
4. **Contacts** - Manage your email lists

## Upgrading

If you need more than 300 emails/day:

- **Lite Plan**: €25/month for 40,000 emails
- **Premium Plan**: €65/month for 120,000 emails
- **Enterprise**: Custom pricing

## API Documentation

For advanced usage, see the [Brevo API documentation](https://developers.brevo.com/docs).

## Migration Benefits

Compared to other services:

- ✅ **No domain verification** (unlike SendGrid, Mailgun)
- ✅ **Works with Railway** (unlike Gmail SMTP)
- ✅ **Free tier available** (unlike some premium services)
- ✅ **HTTPS API** (no SMTP port issues)
- ✅ **Reliable delivery** (established service)

Your email verification system is now ready with Brevo! 🚀

## Next Steps

1. Set up your Brevo account and get API key
2. Update your `.env` file with Brevo credentials
3. Test locally with `test_brevo_email.py`
4. Deploy to Railway with environment variables
5. Test registration on your live application

The system will now send professional verification emails without any domain verification requirements!
