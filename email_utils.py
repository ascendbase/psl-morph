#!/usr/bin/env python3
"""
Email verification system using Resend API
Simple, reliable email sending for user verification
"""

import os
import requests
import secrets
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def send_verification_email(email, token):
    """
    Send verification email using Resend API
    Returns True if successful, False otherwise
    """
    try:
        # Get configuration from environment
        api_key = os.getenv('RESEND_API_KEY')
        from_email = os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
        from_name = os.getenv('RESEND_FROM_NAME', 'PSL Morph')
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
        if not api_key:
            logger.error("RESEND_API_KEY not found in environment variables")
            return False
        
        # Create verification URL
        verification_url = f"{base_url}/auth/verify-email?token={token}"
        
        # Email content
        subject = "Verify Your PSL Morph Account"
        
        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .content h2 {{
                    color: #333;
                    font-size: 24px;
                    margin: 0 0 20px 0;
                }}
                .content p {{
                    margin: 0 0 20px 0;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .verify-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 16px 32px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 16px;
                    transition: transform 0.2s ease;
                }}
                .verify-button:hover {{
                    transform: translateY(-2px);
                }}
                .link-fallback {{
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                    word-break: break-all;
                    font-family: monospace;
                    font-size: 14px;
                    color: #495057;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    border-top: 1px solid #e9ecef;
                }}
                .footer p {{
                    margin: 5px 0;
                    font-size: 14px;
                    color: #6c757d;
                }}
                .logo {{
                    font-size: 32px;
                    font-weight: 700;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎭 PSL Morph</div>
                    <h1>Welcome to PSL Morph!</h1>
                    <p>Please verify your email address to get started</p>
                </div>
                
                <div class="content">
                    <h2>Hi there! 👋</h2>
                    <p>Thank you for signing up for PSL Morph, the advanced facial transformation platform. To complete your registration and start using our cutting-edge AI features, please verify your email address.</p>
                    
                    <div class="button-container">
                        <a href="{verification_url}" class="verify-button">Verify Email Address</a>
                    </div>
                    
                    <p>If the button above doesn't work, you can copy and paste this link into your browser:</p>
                    <div class="link-fallback">{verification_url}</div>
                    
                    <div class="warning">
                        <strong>⏰ Important:</strong> This verification link will expire in 24 hours for security reasons.
                    </div>
                    
                    <p>Once verified, you'll be able to:</p>
                    <ul>
                        <li>🎭 Transform facial features with AI precision</li>
                        <li>📊 Get detailed facial analysis reports</li>
                        <li>🔄 Access advanced morphing tools</li>
                        <li>💎 Enjoy your free credits</li>
                    </ul>
                    
                    <p>If you didn't create an account with PSL Morph, you can safely ignore this email.</p>
                </div>
                
                <div class="footer">
                    <p><strong>© 2024 PSL Morph</strong></p>
                    <p>Advanced AI-Powered Facial Transformation Platform</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version for email clients that don't support HTML
        text_content = f"""
        Welcome to PSL Morph!
        
        Thank you for signing up for our advanced facial transformation platform.
        
        To complete your registration and start using PSL Morph, please verify your email address by visiting:
        
        {verification_url}
        
        This verification link will expire in 24 hours for security reasons.
        
        Once verified, you'll be able to:
        - Transform facial features with AI precision
        - Get detailed facial analysis reports  
        - Access advanced morphing tools
        - Enjoy your free credits
        
        If you didn't create an account with PSL Morph, you can safely ignore this email.
        
        © 2024 PSL Morph - Advanced AI-Powered Facial Transformation Platform
        This is an automated message, please do not reply to this email.
        """
        
        # Prepare email data for Resend API
        email_data = {
            "from": f"{from_name} <{from_email}>",
            "to": [email],
            "subject": subject,
            "html": html_content,
            "text": text_content
        }
        
        # Send email via Resend API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            json=email_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info(f"Verification email sent successfully to {email}")
            return True
        else:
            logger.error(f"Failed to send verification email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")
        return False

def send_welcome_email(email):
    """
    Send welcome email after successful verification
    Returns True if successful, False otherwise
    """
    try:
        # Get configuration from environment
        api_key = os.getenv('RESEND_API_KEY')
        from_email = os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
        from_name = os.getenv('RESEND_FROM_NAME', 'PSL Morph')
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        
        if not api_key:
            logger.error("RESEND_API_KEY not found in environment variables")
            return False
        
        # Email content
        subject = "🎉 Welcome to PSL Morph - Your Account is Ready!"
        
        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to PSL Morph</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .content h2 {{
                    color: #333;
                    font-size: 24px;
                    margin: 0 0 20px 0;
                }}
                .content p {{
                    margin: 0 0 20px 0;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .start-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: white;
                    padding: 16px 32px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 16px;
                    transition: transform 0.2s ease;
                }}
                .start-button:hover {{
                    transform: translateY(-2px);
                }}
                .features {{
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 25px;
                    margin: 25px 0;
                }}
                .features h3 {{
                    color: #333;
                    margin: 0 0 15px 0;
                    font-size: 20px;
                }}
                .features ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .features li {{
                    margin: 8px 0;
                    font-size: 15px;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    border-top: 1px solid #e9ecef;
                }}
                .footer p {{
                    margin: 5px 0;
                    font-size: 14px;
                    color: #6c757d;
                }}
                .logo {{
                    font-size: 32px;
                    font-weight: 700;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎭 PSL Morph</div>
                    <h1>🎉 Welcome to PSL Morph!</h1>
                    <p>Your account is verified and ready to use</p>
                </div>
                
                <div class="content">
                    <h2>Congratulations! 🚀</h2>
                    <p>Your email has been successfully verified and your PSL Morph account is now active. You can now access all our advanced facial transformation features!</p>
                    
                    <div class="button-container">
                        <a href="{base_url}/dashboard" class="start-button">Start Using PSL Morph</a>
                    </div>
                    
                    <div class="features">
                        <h3>🎯 What you can do now:</h3>
                        <ul>
                            <li>🎭 <strong>Transform facial features</strong> - Reshape nose, eyes, lips, and more</li>
                            <li>📊 <strong>Get facial analysis</strong> - Detailed reports on facial structure</li>
                            <li>🔄 <strong>Advanced morphing</strong> - Professional-grade transformation tools</li>
                            <li>💎 <strong>Free credits</strong> - Start with complimentary transformations</li>
                            <li>🎨 <strong>Custom features</strong> - Personalized facial modifications</li>
                        </ul>
                    </div>
                    
                    <p>Need help getting started? Check out our tutorials and guides in your dashboard, or contact our support team if you have any questions.</p>
                    
                    <p>Thank you for choosing PSL Morph for your facial transformation needs!</p>
                </div>
                
                <div class="footer">
                    <p><strong>© 2024 PSL Morph</strong></p>
                    <p>Advanced AI-Powered Facial Transformation Platform</p>
                    <p>Need help? Contact us at support@pslmorph.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        🎉 Welcome to PSL Morph!
        
        Congratulations! Your email has been successfully verified and your PSL Morph account is now active.
        
        You can now access all our advanced facial transformation features:
        
        🎭 Transform facial features - Reshape nose, eyes, lips, and more
        📊 Get facial analysis - Detailed reports on facial structure  
        🔄 Advanced morphing - Professional-grade transformation tools
        💎 Free credits - Start with complimentary transformations
        🎨 Custom features - Personalized facial modifications
        
        Get started: {base_url}/dashboard
        
        Need help getting started? Check out our tutorials and guides in your dashboard.
        
        Thank you for choosing PSL Morph for your facial transformation needs!
        
        © 2024 PSL Morph - Advanced AI-Powered Facial Transformation Platform
        Need help? Contact us at support@pslmorph.com
        """
        
        # Prepare email data for Resend API
        email_data = {
            "from": f"{from_name} <{from_email}>",
            "to": [email],
            "subject": subject,
            "html": html_content,
            "text": text_content
        }
        
        # Send email via Resend API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            json=email_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            logger.info(f"Welcome email sent successfully to {email}")
            return True
        else:
            logger.error(f"Failed to send welcome email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        return False

def validate_email_format(email):
    """
    Basic email format validation
    Returns True if email format is valid, False otherwise
    """
    import re
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or len(email) > 254:
        return False
    
    return bool(re.match(pattern, email))

def is_disposable_email(email):
    """
    Check if email is from a known disposable email provider
    Returns True if disposable, False otherwise
    """
    # Common disposable email domains
    disposable_domains = {
        '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
        'tempmail.org', 'yopmail.com', 'throwaway.email',
        'temp-mail.org', 'getnada.com', 'maildrop.cc',
        'sharklasers.com', 'guerrillamailblock.com'
    }
    
    if not email or '@' not in email:
        return False
    
    domain = email.split('@')[1].lower()
    return domain in disposable_domains

# Compatibility functions for existing code
def send_verification_email_resend(email, token):
    """Alias for send_verification_email for compatibility"""
    return send_verification_email(email, token)

def send_welcome_email_resend(email):
    """Alias for send_welcome_email for compatibility"""
    return send_welcome_email(email)

# Legacy function names for backward compatibility
def send_verification_email_brevo(email, token):
    """Legacy function name - redirects to Resend"""
    return send_verification_email(email, token)

def send_welcome_email_brevo(email):
    """Legacy function name - redirects to Resend"""
    return send_welcome_email(email)
