"""
Forms for user authentication and credit management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    """User registration form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])

class CreditPurchaseForm(FlaskForm):
    """Credit purchase form"""
    package = SelectField('Credit Package', choices=[
        ('100', '100 Credits - $5.00'),
        ('500', '500 Credits - $20.00 (20% bonus)'),
        ('1000', '1000 Credits - $35.00 (30% bonus)')
    ], validators=[DataRequired()])
    
    def get_package_details(self):
        """Get package details based on selection"""
        packages = {
            '100': {'credits': 100, 'price': 5.00, 'bonus': 0},
            '500': {'credits': 500, 'price': 20.00, 'bonus': 100},
            '1000': {'credits': 1000, 'price': 35.00, 'bonus': 300}
        }
        return packages.get(self.package.data, packages['100'])

class AdminUserForm(FlaskForm):
    """Admin form for managing users"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    credits = IntegerField('Credits', validators=[
        NumberRange(min=0, max=10000)
    ], default=0)
    is_admin = BooleanField('Admin User')
    is_active = BooleanField('Active', default=True)

class AdminCreditForm(FlaskForm):
    """Admin form for adding credits to user"""
    user_email = StringField('User Email', validators=[
        DataRequired(),
        Email()
    ])
    credits = IntegerField('Credits to Add', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000)
    ])
    reason = StringField('Reason', validators=[
        Length(max=200)
    ])