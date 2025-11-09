from flask import Flask, render_template, Blueprint

app = Flask(__name__, template_folder='templates')

# Create dummy blueprints
auth_bp = Blueprint('auth', __name__)
payments_bp = Blueprint('payments', __name__)

@app.route('/dashboard')
def dashboard():
    # Mock data to prevent template errors
    stats = {
        'total_generations': 0,
        'successful_generations': 0,
        'credits_used': 0,
        'credits_remaining': 0,
        'free_generations_remaining': 0
    }
    return render_template('dashboard.html', stats=stats, recent_generations=[], current_user={'is_admin': False, 'email': 'test@test.com'})

@app.route('/admin/dashboard')
def admin_dashboard():
    return "Admin Dashboard"

@auth_bp.route('/profile')
def profile():
    return "User Profile"

@auth_bp.route('/logout')
def logout():
    return "Logout"

@app.route('/app_interface')
def app_interface():
    return "App Interface"

@app.route('/facial_evaluation_dashboard')
def facial_evaluation_dashboard():
    return "Facial Evaluation Dashboard"

@payments_bp.route('/buy_credits')
def buy_credits():
    return "Buy Credits"

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(payments_bp, url_prefix='/payments')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
