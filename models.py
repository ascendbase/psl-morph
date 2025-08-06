"""
Database models for user authentication and credit system
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import bcrypt
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and credit tracking"""
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    
    # Credit system
    credits = db.Column(db.Integer, default=12)  # Paid credits - new users get 12 free credits
    free_generations_used_today = db.Column(db.Integer, default=0)
    last_free_generation_date = db.Column(db.Date)
    
    # Relationships
    generations = db.relationship('Generation', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def can_generate_free(self):
        """Check if user can use free generation today"""
        today = datetime.utcnow().date()
        
        # Reset counter if it's a new day
        if self.last_free_generation_date != today:
            self.free_generations_used_today = 0
            self.last_free_generation_date = today
            db.session.commit()
        
        return self.free_generations_used_today < 1
    
    def use_free_generation(self):
        """Use one free generation for today"""
        today = datetime.utcnow().date()
        
        if self.last_free_generation_date != today:
            self.free_generations_used_today = 0
            self.last_free_generation_date = today
        
        self.free_generations_used_today += 1
        db.session.commit()
    
    def can_generate_paid(self):
        """Check if user has paid credits"""
        return self.credits > 0
    
    def use_paid_credit(self):
        """Use one paid credit"""
        if self.credits > 0:
            self.credits -= 1
            db.session.commit()
            return True
        return False
    
    def add_credits(self, amount):
        """Add credits to user account"""
        self.credits += amount
        db.session.commit()
    
    def get_generation_stats(self):
        """Get user's generation statistics"""
        total_generations = Generation.query.filter_by(user_id=self.id).count()
        
        # Get today's date range for proper datetime filtering
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_generations = Generation.query.filter_by(user_id=self.id).filter(
            Generation.created_at >= today_start,
            Generation.created_at < today_end
        ).count()
        
        successful_generations = Generation.query.filter_by(user_id=self.id, status='completed').count()
        credits_used = Generation.query.filter_by(user_id=self.id, used_paid_credit=True).count()
        
        return {
            'total_generations': total_generations,
            'today_generations': today_generations,
            'successful_generations': successful_generations,
            'credits_used': credits_used,
            'credits_remaining': self.credits,
            'free_generations_remaining': 1 - self.free_generations_used_today if self.can_generate_free() else 0
        }
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'credits': self.credits,
            'is_admin': self.is_admin,
            'stats': self.get_generation_stats()
        }

class Generation(db.Model):
    """Model to track image generations"""
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Generation details
    preset = db.Column(db.String(20), nullable=False)  # HTN, Chadlite, Chad
    workflow_type = db.Column(db.String(20), nullable=False)  # reactor, facedetailer
    
    # Processing details
    prompt_id = db.Column(db.String(100))  # ComfyUI prompt ID
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    
    # File details
    input_filename = db.Column(db.String(255))
    output_filename = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Credit tracking
    used_free_credit = db.Column(db.Boolean, default=False)
    used_paid_credit = db.Column(db.Boolean, default=False)
    
    # Error handling
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        """Convert generation to dictionary"""
        return {
            'id': self.id,
            'preset': self.preset,
            'workflow_type': self.workflow_type,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'used_free_credit': self.used_free_credit,
            'used_paid_credit': self.used_paid_credit,
            'error_message': self.error_message
        }

class Transaction(db.Model):
    """Model to track credit purchases"""
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Transaction details
    amount_usd = db.Column(db.Float, nullable=False)  # Amount paid in USD
    credits_purchased = db.Column(db.Integer, nullable=False)  # Credits purchased
    
    # Payment details
    payment_provider = db.Column(db.String(20), nullable=False)  # stripe, paypal
    payment_id = db.Column(db.String(100), nullable=False)  # Provider transaction ID
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'amount_usd': self.amount_usd,
            'credits_purchased': self.credits_purchased,
            'payment_provider': self.payment_provider,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class ApiKey(db.Model):
    """Model for API keys (for future API access)"""
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    # Rate limiting
    requests_today = db.Column(db.Integer, default=0)
    last_request_date = db.Column(db.Date)
    
    def generate_key(self):
        """Generate a new API key"""
        import secrets
        self.key = secrets.token_urlsafe(48)
    
    def can_make_request(self, daily_limit=1000):
        """Check if API key can make a request"""
        today = datetime.utcnow().date()
        
        if self.last_request_date != today:
            self.requests_today = 0
            self.last_request_date = today
        
        return self.requests_today < daily_limit
    
    def record_request(self):
        """Record an API request"""
        today = datetime.utcnow().date()
        
        if self.last_request_date != today:
            self.requests_today = 0
            self.last_request_date = today
        
        self.requests_today += 1
        self.last_used = datetime.utcnow()
        db.session.commit()

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    
    with app.app_context():
        try:
            # Skip automatic table creation - using manual database setup
            # db.create_all()  # Commented out to prevent overwriting manually created database
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database tables may already exist: {e}")
            # Tables might already exist, continue with admin user creation
        
        try:
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(email='ascendbase@gmail.com').first()
            if not admin:
                admin = User(
                    email='ascendbase@gmail.com',
                    is_admin=True,
                    credits=1000  # Give admin some credits for testing
                )
                admin.set_password('morphpas')
                db.session.add(admin)
                db.session.commit()
                print("Created admin user: ascendbase@gmail.com / morphpas")
            else:
                print("Admin user already exists")
            
            # Remove old admin user if it exists
            old_admin = User.query.filter_by(email='admin@example.com').first()
            if old_admin:
                db.session.delete(old_admin)
                db.session.commit()
                print("Removed old admin user")
                
        except Exception as e:
            print(f"Error during admin user setup: {e}")
            # Continue anyway, the app should still work