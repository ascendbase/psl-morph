"""
Payment processing for credit purchases
Supports crypto payments only
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Transaction
from forms import CreditPurchaseForm
from config import CREDIT_PACKAGES
import logging
from datetime import datetime
import uuid
import hashlib

logger = logging.getLogger(__name__)

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

# Crypto payment addresses (replace with your actual addresses)
CRYPTO_ADDRESSES = {
    'USDT_TRC20': '0x0812ddaa78523754a390887827cf6baf50ae2e9a',
    'BTC': '16AAhHerKz58zENs4seMtAJYKzw1R1JHy7',
    'ETH': '0x0812ddaa78523754a390887827cf6baf50ae2e9a'
}


@payments_bp.route('/buy-credits', methods=['GET', 'POST'])
@login_required
def buy_credits():
    """Credit purchase page with crypto payments only"""
    if request.method == 'POST':
        # Handle payment form submission
        package_id = request.form.get('package')
        payment_method = request.form.get('payment_method')
        
        if not package_id or package_id not in CREDIT_PACKAGES:
            flash('Invalid credit package selected', 'error')
            return redirect(url_for('payments.buy_credits'))
        
        if not payment_method or payment_method != 'crypto':
            flash('Invalid payment method selected', 'error')
            return redirect(url_for('payments.buy_credits'))
        
        package = CREDIT_PACKAGES[package_id]
        
        # Create pending transaction
        transaction = Transaction(
            user_id=current_user.id,
            amount_usd=package['price'],
            credits_purchased=package['credits'] + package.get('bonus', 0),
            payment_provider='crypto',
            payment_id=f"crypto_{uuid.uuid4().hex[:8]}",
            payment_status='pending'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        logger.info(f"Crypto payment initiated: {transaction.id} for user {current_user.email}")
        
        # Redirect to payment success page
        return render_template('payments/payment_success.html',
                             transaction=transaction)
    
    # GET request - show the form
    form = CreditPurchaseForm()
    
    # Prepare crypto wallets for template
    crypto_wallets = {
        'btc': CRYPTO_ADDRESSES.get('BTC', '16AAhHerKz58zENs4seMtAJYKzw1R1JHy7'),
        'eth': CRYPTO_ADDRESSES.get('ETH', '0x0812ddaa78523754a390887827cf6baf50ae2e9a'),
        'usdt': CRYPTO_ADDRESSES.get('USDT_TRC20', '0x0812ddaa78523754a390887827cf6baf50ae2e9a')
    }
    
    return render_template('payments/buy_credits.html',
                         form=form,
                         credit_packages=CREDIT_PACKAGES,
                         crypto_wallets=crypto_wallets)

@payments_bp.route('/crypto-payment', methods=['POST'])
@login_required
def crypto_payment():
    """Generate crypto payment details"""
    try:
        data = request.get_json()
        package_id = data.get('package')
        crypto_type = data.get('crypto_type')
        
        if package_id not in CREDIT_PACKAGES:
            return jsonify({'error': 'Invalid package'}), 400
        
        if crypto_type not in CRYPTO_ADDRESSES:
            return jsonify({'error': 'Invalid crypto type'}), 400
        
        package = CREDIT_PACKAGES[package_id]
        
        # Create pending transaction
        transaction = Transaction(
            user_id=current_user.id,
            amount_usd=package['price'],
            credits_purchased=package['credits'] + package['bonus'],
            payment_provider='crypto',
            payment_id=f"crypto_{uuid.uuid4().hex[:8]}",
            payment_status='pending'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Generate payment reference
        payment_ref = f"MORPH-{current_user.id[:8]}-{package_id}-{transaction.id[:8]}"
        
        logger.info(f"Crypto payment initiated: {transaction.id} for user {current_user.email}")
        
        return jsonify({
            'transaction_id': transaction.id,
            'address': CRYPTO_ADDRESSES[crypto_type],
            'amount_usd': package['price'],
            'crypto_type': crypto_type,
            'reference': payment_ref,
            'credits': package['credits'] + package['bonus'],
            'instructions': get_crypto_instructions(crypto_type, package['price'])
        })
        
    except Exception as e:
        logger.error(f"Error creating crypto payment: {e}")
        return jsonify({'error': 'Payment setup failed'}), 500


@payments_bp.route('/verify-payment', methods=['POST'])
@login_required
def verify_payment():
    """Submit payment verification (manual process)"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        payment_proof = data.get('payment_proof', '')  # Transaction hash or reference
        
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=current_user.id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        if transaction.payment_status != 'pending':
            return jsonify({'error': 'Transaction already processed'}), 400
        
        # Update transaction with proof
        transaction.payment_id = payment_proof or transaction.payment_id
        transaction.payment_status = 'verification_pending'
        db.session.commit()
        
        logger.info(f"Payment verification submitted: {transaction_id} by {current_user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Payment verification submitted. Credits will be added within 24 hours after verification.'
        })
        
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return jsonify({'error': 'Verification failed'}), 500

@payments_bp.route('/payment-status/<transaction_id>')
@login_required
def payment_status(transaction_id):
    """Check payment status"""
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=current_user.id
    ).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    return jsonify({
        'status': transaction.payment_status,
        'amount': transaction.amount_usd,
        'credits': transaction.credits_purchased,
        'created_at': transaction.created_at.isoformat(),
        'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None
    })

def get_crypto_instructions(crypto_type, amount):
    """Get crypto payment instructions"""
    instructions = {
        'USDT_TRC20': f"Send exactly ${amount} worth of USDT (TRC-20) to the address above. Include the reference in the transaction memo if possible.",
        'BTC': f"Send exactly ${amount} worth of BTC to the address above. Transaction will be verified automatically.",
        'ETH': f"Send exactly ${amount} worth of ETH to the address above. Transaction will be verified automatically."
    }
    return instructions.get(crypto_type, "Send the exact USD equivalent to the address above.")


# Admin routes for manual payment verification
@payments_bp.route('/admin/pending-payments')
@login_required
def admin_pending_payments():
    """Admin page to verify pending payments"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    pending_transactions = Transaction.query.filter_by(
        payment_status='verification_pending'
    ).order_by(Transaction.created_at.desc()).all()
    
    return render_template('payments/admin_pending.html', 
                         transactions=pending_transactions)

@payments_bp.route('/admin/approve-payment/<transaction_id>', methods=['POST'])
@login_required
def admin_approve_payment(transaction_id):
    """Admin approve payment"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    if transaction.payment_status not in ['pending', 'verification_pending']:
        return jsonify({'error': 'Transaction not pending verification'}), 400
    
    # Approve payment and add credits
    user = User.query.get(transaction.user_id)
    user.add_credits(transaction.credits_purchased)
    
    transaction.payment_status = 'completed'
    transaction.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    logger.info(f"Payment approved by admin: {transaction_id}, credits added to {user.email}")
    
    return jsonify({'success': True, 'message': 'Payment approved and credits added'})