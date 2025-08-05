"""
Authentication routes and user management
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Generation, Transaction
from forms import LoginForm, RegisterForm, ChangePasswordForm
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
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
    """User registration"""
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
            flash('Email address already registered', 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(email=email)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {user.email}")
        flash('Registration successful! You can now log in.', 'success')
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