# Email Verification Setup Guide for PSL Morph

This guide explains how to set up email verification for user registration using Resend API, which is free, unlimited for reasonable usage, works perfectly with Railway, and doesn't require domain configuration.

## Overview

The email verification system prevents abuse by requiring users to verify their email addresses before they can log in and use the application. This helps prevent users from creating infinite accounts to get free credits.

## Features Implemented

✅ **Email verification on registration**
- Users must verify their email before logging in
- Verification emails sent automatically on registration
- Beautiful HTML email templates with PSL Morph branding

✅ **Secure verification tokens**
- Cryptographically secure tokens generated for each user
- Tokens expire after 24 hours for security
- Tokens are cleared after successful verification

✅ **Resend verification functionality**
- Users can request new verification emails if needed
- Dedicated resend verification page
- Prevents spam by checking if user is already verified

✅ **Welcome emails**
- Automatic welcome email sent after successful verification
- Includes helpful information about account features

✅ **Database integration**
- Added `is_verified` and `verification_token` columns to User model
- Proper database constraints and defaults

## Setup Instructions

### 1. Sign up for Resend (Free)

1. Go to [https://resend.com](https://resend.com)
2. Sign up for a free account (no credit card required)
3. Verify your email address
4. Go to the API Keys section in your dashboard
5. Create a new API key
6. Copy the API key (starts with `re_`)

### 2. Configure Environment Variables

Update your `.env` file with the Resend API key:

```env
# Resend API Configuration (Free email service that works with Railway)
RESEND_API_KEY=re_your_actual_api_key_here

# Base URL for email verification links
BASE_URL=https://psl-morph-production.up.railway.app
```

### 3. Railway Environment Variables

In your Railway dashboard:

1. Go to your project settings
2. Navigate to the Variables tab
3. Add the following environment variables:
   - `RESEND_API_KEY`: Your Resend API key
   - `BASE_URL`: Your Railway app URL (e.g., `https://psl-morph-production.up.railway.app`)

### 4. Database Migration

The database schema has been updated to include email verification fields. If you're deploying to Railway, the database will be automatically updated when you deploy.

For local development, you may need to update your database schema:

```sql
ALTER TABLE "user" ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE "user" ADD COLUMN verification_token VARCHAR(100);
```

## How It Works

### Registration Flow

1. **User registers** with email and password
2. **System creates user** with `is_verified=False`
3. **Verification token generated** and stored in database
4. **Verification email sent** via Resend API
5. **User receives email** with verification link
6. **User clicks link** to verify email
7. **System verifies token** and marks user as verified
8. **Welcome email sent** to confirmed user

### Login Flow

1. **User attempts login** with email and password
2. **System checks credentials** (email/password)
3. **System checks verification status**
4. **If not verified**: Login blocked with message to check email
5. **If verified**: Login proceeds normally

### Email Templates

The system includes beautiful HTML email templates:

- **Verification Email**: Professional design with clear call-to-action button
- **Welcome Email**: Welcoming message with feature overview
- **Responsive Design**: Works on desktop and mobile devices
- **PSL Morph Branding**: Consistent with app design

## Security Features

### Token Security
- **Cryptographically secure tokens** using `secrets.token_urlsafe(32)`
- **24-hour expiration** for verification links
- **One-time use tokens** (cleared after verification)

### Abuse Prevention
- **Email verification required** before login
- **Gmail-only registration** (as per existing requirement)
- **Duplicate registration prevention** with helpful messages
- **Rate limiting** through Resend's built-in protections

### Database Security
- **Proper indexing** on email and verification_token fields
- **Nullable verification_token** (cleared after use)
- **Boolean is_verified** with proper default

## API Endpoints

### Authentication Routes

- `POST /auth/register` - User registration with email verification
- `POST /auth/login` - Login with verification check
- `GET /auth/verify-email?token=<token>` - Email verification endpoint
- `GET /auth/resend-verification` - Resend verification form
- `POST /auth/resend-verification` - Resend verification email

### User Experience

- **Clear messaging** at each step of the process
- **Helpful error messages** for common issues
- **Resend functionality** for lost emails
- **Tips and troubleshooting** information

## Testing

### Local Testing

1. Set up Resend API key in your local `.env` file
2. Set `BASE_URL=http://localhost:5000` for local testing
3. Register a new user with your email
4. Check your email for verification link
5. Click the link to verify

### Production Testing

1. Deploy to Railway with proper environment variables
2. Register with a test Gmail account
3. Verify the complete flow works end-to-end

## Troubleshooting

### Common Issues

**Email not received:**
- Check spam/junk folder
- Verify Resend API key is correct
- Check Resend dashboard for delivery status

**Verification link expired:**
- Links expire after 24 hours
- Use the resend verification feature
- Register again if needed

**Railway deployment issues:**
- Ensure environment variables are set correctly
- Check Railway logs for any errors
- Verify database connection

### Support

If you encounter issues:
1. Check the Railway logs for error messages
2. Verify all environment variables are set
3. Test with a different email address
4. Contact Resend support if email delivery fails

## Benefits

### For Users
- **Secure account creation** with verified email addresses
- **Professional email experience** with branded templates
- **Clear instructions** and helpful error messages

### For Administrators
- **Abuse prevention** - no more infinite account creation
- **Verified user base** - all users have valid email addresses
- **Reliable email delivery** through Resend's infrastructure

### For Developers
- **Simple integration** with existing Flask-Login system
- **Scalable solution** that works with Railway
- **No domain configuration** required
- **Free tier** sufficient for most applications

## Conclusion

The email verification system is now fully implemented and ready for production use. It provides a robust, secure, and user-friendly way to verify email addresses while preventing abuse of the free credit system.

The integration with Resend ensures reliable email delivery without the complexity of setting up your own SMTP server or dealing with Gmail's restrictions on Railway.
