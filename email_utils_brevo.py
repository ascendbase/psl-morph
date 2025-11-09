"""
Email utilities for sending verification emails using Brevo (Sendinblue) API
Brevo works reliably with Railway through HTTPS and doesn't require domain verification
"""

import os
import secrets
import requests
import logging
from flask import url_for, current_app

logger = logging.getLogger(__name__)

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def send_verification_email(user_email, verification_token):
    """
    Send verification email using Brevo API
    
    Args:
        user_email (str): User's email address
        verification_token (str): Verification token
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get Brevo configuration from environment
        brevo_api_key = os.getenv('BREVO_API_KEY')
        from_email = os.getenv('BREVO_FROM_EMAIL', 'noreply@example.com')
        from_name = os.getenv('BREVO_FROM_NAME', 'PSL Morph')
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
        if not brevo_api_key:
            logger.error("Brevo configuration missing: Please set BREVO_API_KEY")
            return False
        
        # Create verification URL
        verification_url = f"{base_url}/auth/verify-email?token={verification_token}"
        
        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email - PSL Morph</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .verify-button {{
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .verify-button:hover {{
            background-color: #2980b9;
        }}
        .features {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .feature-item {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">PSL Morph</div>
            <h2>Welcome! Please verify your email</h2>
        </div>
        
        <p>Thank you for registering with PSL Morph. To complete your registration and start using our AI-powered face morphing services, please verify your email address.</p>
        
        <div style="text-align: center;">
            <a href="{verification_url}" class="verify-button">Verify Email Address</a>
        </div>
        
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 5px;">{verification_url}</p>
        
        <p><strong>This verification link will expire in 24 hours.</strong></p>
        
        <div class="features">
            <h3>Once verified, you'll be able to:</h3>
            <div class="feature-item">💎 Get 5 free credits to start your journey</div>
            <div class="feature-item">🎯 Access premium morphing presets (HTN, Chadlite, Chad)</div>
            <div class="feature-item">📊 Request professional facial evaluations</div>
            <div class="feature-item">🔄 Get one free generation every day</div>
        </div>
        
        <p>If you didn't create an account with PSL Morph, please ignore this email.</p>
        
        <div class="footer">
            <p>Best regards,<br>The PSL Morph Team</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Create plain text version
        text_content = f"""
Welcome to PSL Morph!

Thank you for registering with PSL Morph. To complete your registration and start using our face morphing services, please verify your email address.

Click the link below to verify your email:
{verification_url}

This verification link will expire in 24 hours.

Once verified, you'll be able to:
- Transform your photos with AI-powered face morphing
- Access premium morphing presets (HTN, Chadlite, Chad)
- Get 5 free credits to start your journey
- Request professional facial evaluations

If you didn't create an account with PSL Morph, please ignore this email.

Best regards,
The PSL Morph Team
        """
        
        # Prepare email data for Brevo API
        email_data = {
            "sender": {
                "name": from_name,
                "email": from_email
            },
            "to": [
                {
                    "email": user_email,
                    "name": user_email.split('@')[0]
                }
            ],
            "subject": "Verify Your Email - PSL Morph",
            "htmlContent": html_content,
            "textContent": text_content
        }
        
        # Send email via Brevo API
        headers = {
            "accept": "application/json",
            "api-key": brevo_api_key,
            "content-type": "application/json"
        }
        
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=email_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            logger.info(f"Verification email sent successfully to {user_email}")
            return True
        else:
            logger.error(f"Failed to send verification email to {user_email}. Status: {response.status_code}, Response: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user_email}: {str(e)}")
        return False

def send_welcome_email(user_email):
    """
    Send welcome email after successful verification using Brevo API
    
    Args:
        user_email (str): User's email address
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get Brevo configuration from environment
        brevo_api_key = os.getenv('BREVO_API_KEY')
        from_email = os.getenv('BREVO_FROM_EMAIL', 'noreply@example.com')
        from_name = os.getenv('BREVO_FROM_NAME', 'PSL Morph')
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
        if not brevo_api_key:
            logger.error("Brevo configuration missing for welcome email")
            return False
        
        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to PSL Morph</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .success-icon {{
            font-size: 48px;
            margin: 20px 0;
        }}
        .dashboard-button {{
            display: inline-block;
            background-color: #27ae60;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .dashboard-button:hover {{
            background-color: #229954;
        }}
        .features {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .feature-item {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">PSL Morph</div>
            <div class="success-icon">🎉</div>
            <h2>Congratulations! Your account is ready</h2>
        </div>
        
        <p>Your email has been successfully verified and your PSL Morph account is now active. You're ready to start your face transformation journey!</p>
        
        <div style="text-align: center;">
            <a href="{base_url}/dashboard" class="dashboard-button">Go to Dashboard</a>
        </div>
        
        <div class="features">
            <h3>What's included with your account:</h3>
            <div class="feature-item">💎 <strong>5 Free Credits</strong> - Start exploring our AI-powered face morphing technology</div>
            <div class="feature-item">🎯 <strong>Premium Morphing Presets</strong> - Access to HTN, Chadlite, and Chad transformation presets</div>
            <div class="feature-item">📊 <strong>Professional Evaluations</strong> - Request detailed facial evaluations from our expert team</div>
            <div class="feature-item">🔄 <strong>Daily Free Generation</strong> - Get one free generation every day, even after using your initial credits</div>
        </div>
        
        <p>Ready to get started? Visit your dashboard and begin transforming your photos with our advanced AI technology.</p>
        
        <p>If you have any questions or need help, don't hesitate to reach out to our support team.</p>
        
        <div class="footer">
            <p>Best regards,<br>The PSL Morph Team</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Create plain text version
        text_content = f"""
Congratulations! 🎉

Your email has been successfully verified and your PSL Morph account is now active. You're ready to start your face transformation journey!

What's included with your account:

💎 5 Free Credits
Start exploring our AI-powered face morphing technology with 5 complimentary credits.

🎯 Premium Morphing Presets
Access to HTN, Chadlite, and Chad transformation presets for different enhancement levels.

📊 Professional Evaluations
Request detailed facial evaluations from our expert team.

🔄 Daily Free Generation
Get one free generation every day, even after using your initial credits.

Ready to get started? Visit your dashboard: {base_url}/dashboard

If you have any questions or need help, don't hesitate to reach out to our support team.

Best regards,
The PSL Morph Team
        """
        
        # Prepare email data for Brevo API
        email_data = {
            "sender": {
                "name": from_name,
                "email": from_email
            },
            "to": [
                {
                    "email": user_email,
                    "name": user_email.split('@')[0]
                }
            ],
            "subject": "Welcome to PSL Morph - Your Account is Ready!",
            "htmlContent": html_content,
            "textContent": text_content
        }
        
        # Send email via Brevo API
        headers = {
            "accept": "application/json",
            "api-key": brevo_api_key,
            "content-type": "application/json"
        }
        
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=email_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            logger.info(f"Welcome email sent successfully to {user_email}")
            return True
        else:
            logger.error(f"Failed to send welcome email to {user_email}. Status: {response.status_code}, Response: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
        return False
