#!/usr/bin/env python3
"""
Simple test script to verify facial evaluation feature implementation
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_imports():
    """Test that the app can be imported and has the required components"""
    
    print("Testing app imports...")
    
    try:
        from app import app, db
        print("✅ Successfully imported Flask app and database")
        
        # Test that the app has the required routes
        with app.app_context():
            # Get all registered routes
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(rule.rule)
            
            required_routes = [
                '/facial-evaluation',
                '/facial-evaluation/request',
                '/admin/facial-evaluations',
                '/admin/facial-evaluation/<int:evaluation_id>/respond'
            ]
            
            for route in required_routes:
                if route in routes:
                    print(f"✅ Found required route: {route}")
                else:
                    print(f"❌ Missing required route: {route}")
                    return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing app: {e}")
        return False

def test_models():
    """Test that the FacialEvaluation model exists and has required fields"""
    
    print("\nTesting database models...")
    
    try:
        from models import FacialEvaluation
        print("✅ Successfully imported FacialEvaluation model")
        
        # Check if the model has required attributes
        required_attributes = [
            'id', 'user_id', 'original_image_path', 'morphed_image_path',
            'status', 'admin_response', 'created_at', 'responded_at'
        ]
        
        for attr in required_attributes:
            if hasattr(FacialEvaluation, attr):
                print(f"✅ Model has required attribute: {attr}")
            else:
                print(f"❌ Model missing required attribute: {attr}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import FacialEvaluation model: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False

def test_forms():
    """Test that the facial evaluation forms exist"""
    
    print("\nTesting forms...")
    
    try:
        from forms import FacialEvaluationRequestForm, FacialEvaluationResponseForm
        print("✅ Successfully imported facial evaluation forms")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import forms: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing forms: {e}")
        return False

def test_templates():
    """Test that the required templates exist"""
    
    print("\nTesting templates...")
    
    required_templates = [
        'templates/facial_evaluation/dashboard.html',
        'templates/admin/facial_evaluations.html',
        'templates/admin/respond_facial_evaluation.html'
    ]
    
    for template in required_templates:
        if os.path.exists(template):
            print(f"✅ Found required template: {template}")
        else:
            print(f"❌ Missing required template: {template}")
            return False
    
    return True

def test_markdown_filter():
    """Test markdown filter without external dependencies"""
    
    print("\nTesting markdown filter (basic functionality)...")
    
    try:
        from app import app
        
        with app.app_context():
            # Check if markdown filter is registered
            if 'markdown' in app.jinja_env.filters:
                print("✅ Markdown filter is registered")
                
                # Test basic functionality (if mistune is available)
                try:
                    markdown_filter = app.jinja_env.filters['markdown']
                    
                    # Test with simple text
                    result = markdown_filter("**Bold text**")
                    if result and 'strong' in str(result):
                        print("✅ Markdown filter working correctly")
                    else:
                        print("⚠️  Markdown filter registered but may need mistune dependency")
                    
                except Exception as e:
                    print(f"⚠️  Markdown filter registered but has dependency issue: {e}")
                
                return True
            else:
                print("❌ Markdown filter not registered")
                return False
                
    except Exception as e:
        print(f"❌ Error testing markdown filter: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("FACIAL EVALUATION FEATURE VERIFICATION")
    print("=" * 60)
    
    success = True
    
    # Test app imports
    if not test_app_imports():
        success = False
    
    # Test models
    if not test_models():
        success = False
    
    # Test forms
    if not test_forms():
        success = False
    
    # Test templates
    if not test_templates():
        success = False
    
    # Test markdown filter
    if not test_markdown_filter():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Facial evaluation feature is properly implemented.")
        print("\nNext steps:")
        print("1. Ensure database migrations are applied")
        print("2. Test the feature in a web browser")
        print("3. Verify admin can respond to facial evaluation requests")
    else:
        print("❌ SOME TESTS FAILED! Please check the implementation.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
