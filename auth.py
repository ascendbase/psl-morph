"""
Authentication routes and user management
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Generation, Transaction
from forms import LoginForm, RegisterForm, ChangePasswordForm
from email_utils import generate_verification_token, send_verification_email, send_welcome_email
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)
            
            if user.is_blocked:
                flash('Your account has been blocked. Please contact support at ascendbase@gmail.com.', 'error')
                return render_template('auth/login.html', form=form)
            
            if not user.is_verified:
                flash('Please verify your email address before logging in. Check your email for the verification link, or <a href="/auth/resend-verification">click here to resend verification email</a>.', 'warning')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"User logged in: {user.email}")
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email verification"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        
        # Check if email is Gmail
        if not email.endswith('@gmail.com'):
            flash('Only Gmail accounts are allowed to register. Please use a @gmail.com email address.', 'error')
            return render_template('auth/register.html', form=form)
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.is_verified:
                flash('Email address already registered and verified. Please log in.', 'error')
            else:
                flash('Email address already registered but not verified. Please check your email for verification link.', 'warning')
            return render_template('auth/register.html', form=form)
        
        # Generate verification token
        verification_token = generate_verification_token()
        
        # Create new user (not verified initially)
        user = User(
            email=email,
            is_verified=False,
            verification_token=verification_token,
            verification_token_created_at=datetime.utcnow()
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        if send_verification_email(email, verification_token):
            logger.info(f"New user registered: {user.email}, verification email sent")
            flash('Registration successful! Please check your email and click the verification link to activate your account.', 'success')
        else:
            logger.error(f"Failed to send verification email to {user.email}")
            flash('Registration successful, but we could not send the verification email. Please contact support.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logger.info(f"User logged out: {current_user.email}")
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    stats = current_user.get_generation_stats()
    recent_generations = Generation.query.filter_by(user_id=current_user.id)\
        .order_by(Generation.created_at.desc()).limit(10).all()
    
    # Get recent transactions for payment status
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).limit(10).all()
    
    return render_template('auth/profile.html',
                         user=current_user,
                         stats=stats,
                         recent_generations=recent_generations,
                         recent_transactions=recent_transactions)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'error')
            return render_template('auth/change_password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        flash('Password changed successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/verify-email')
def verify_email():
    """Email verification endpoint"""
    token = request.args.get('token')
    
    if not token:
        flash('Invalid verification link.', 'error')
        return redirect(url_for('auth.login'))
    
    # Find user with this verification token
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash('Invalid or expired verification link.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash('Email already verified. You can log in now.', 'info')
        return redirect(url_for('auth.login'))
    
    # Check if token is expired (24 hours)
    if user.verification_token_created_at and user.verification_token_created_at < datetime.utcnow() - timedelta(hours=24):
        flash('Verification link has expired. Please request a new verification email.', 'error')
        return redirect(url_for('auth.resend_verification'))
    elif not user.verification_token_created_at and user.created_at < datetime.utcnow() - timedelta(hours=24):
        # Fallback for old tokens without timestamp
        flash('Verification link has expired. Please request a new verification email.', 'error')
        return redirect(url_for('auth.resend_verification'))
    
    # Verify the user
    user.is_verified = True
    user.verification_token = None  # Clear the token
    db.session.commit()
    
    # Send welcome email
    send_welcome_email(user.email)
    
    logger.info(f"User email verified: {user.email}")
    flash('Email verified successfully! You can now log in and start using PSL Morph.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend verification email"""
    if request.method == 'GET':
        return render_template('auth/resend_verification.html')
    
    email = request.form.get('email', '').lower().strip()
    
    if not email:
        flash('Please enter your email address.', 'error')
        return render_template('auth/resend_verification.html')
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('No account found with this email address.', 'error')
        return render_template('auth/resend_verification.html')
    
    if user.is_verified:
        flash('Email already verified. You can log in now.', 'info')
        return redirect(url_for('auth.login'))
    
    # Generate new verification token
    verification_token = generate_verification_token()
    user.verification_token = verification_token
    user.verification_token_created_at = datetime.utcnow()
    db.session.commit()
    
    # Send verification email
    if send_verification_email(email, verification_token):
        logger.info(f"Verification email resent to: {email}")
        flash('Verification email sent! Please check your email and click the verification link.', 'success')
    else:
        logger.error(f"Failed to resend verification email to {email}")
        flash('Failed to send verification email. Please try again later or contact support.', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/user-info')
@login_required
def api_user_info():
    """API endpoint for user information"""
    return jsonify({
        'user': current_user.to_dict(),
        'stats': current_user.get_generation_stats()
    })

@auth_bp.route('/api/check-credits')
@login_required
def api_check_credits():
    """API endpoint to check if user can generate"""
    can_free = current_user.can_generate_free()
    can_paid = current_user.can_generate_paid()
    
    return jsonify({
        'can_generate_free': can_free,
        'can_generate_paid': can_paid,
        'credits': current_user.credits,
        'free_generations_remaining': 1 - current_user.free_generations_used_today if can_free else 0,
        'message': get_credit_message(can_free, can_paid, current_user.credits)
    })

def get_credit_message(can_free, can_paid, credits):
    """Get appropriate message for credit status"""
    if can_free:
        return "You have 1 free generation available today!"
    elif can_paid:
        return f"You have {credits} paid credits remaining"
    else:
        return "No credits available. Purchase credits or wait until tomorrow for your free generation."

# User loader for Flask-Login
from flask_login import LoginManager

def init_login_manager(app):
    """Initialize Flask-Login"""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    return login_manager
