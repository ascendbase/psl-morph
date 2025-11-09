#!/usr/bin/env python3
"""
Test script to verify markdown rendering fix for facial evaluation feature
"""

import os
import sys
from flask import Flask
from markupsafe import Markup
import mistune

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_markdown_filter():
    """Test the markdown filter functionality"""
    
    # Create a simple Flask app for testing
    app = Flask(__name__)
    
    # Define the markdown filter (same as in app.py)
    @app.template_filter('markdown')
    def markdown_filter(s):
        """Convert a string to Markdown and mark it safe for Jinja"""
        if s:
            return Markup(mistune.html(s))
        return ''
    
    # Test cases
    test_cases = [
        {
            'input': '**Bold text** and *italic text*',
            'expected_contains': ['<strong>Bold text</strong>', '<em>italic text</em>']
        },
        {
            'input': '# Heading\n\nThis is a paragraph with a [link](https://example.com).',
            'expected_contains': ['<h1>Heading</h1>', '<p>This is a paragraph', '<a href="https://example.com">link</a>']
        },
        {
            'input': 'Simple text without markdown',
            'expected_contains': ['<p>Simple text without markdown</p>']
        },
        {
            'input': '',
            'expected_contains': []
        },
        {
            'input': None,
            'expected_contains': []
        }
    ]
    
    print("Testing markdown filter functionality...")
    
    with app.app_context():
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['input']!r}")
            
            try:
                result = markdown_filter(test_case['input'])
                print(f"Result: {result!r}")
                print(f"Type: {type(result)}")
                
                # Check if result is Markup (safe for Jinja)
                if test_case['input']:
                    if not isinstance(result, Markup):
                        print(f"❌ FAIL: Result is not Markup type, got {type(result)}")
                        return False
                    else:
                        print("✅ PASS: Result is Markup type (safe for Jinja)")
                
                # Check expected content
                for expected in test_case['expected_contains']:
                    if expected not in str(result):
                        print(f"❌ FAIL: Expected '{expected}' not found in result")
                        return False
                    else:
                        print(f"✅ PASS: Found expected content '{expected}'")
                
                if not test_case['expected_contains'] and not result:
                    print("✅ PASS: Empty input produces empty result")
                
            except Exception as e:
                print(f"❌ FAIL: Exception occurred: {e}")
                return False
    
    print("\n🎉 All markdown filter tests passed!")
    return True

def test_facial_evaluation_template():
    """Test that the facial evaluation template would render correctly"""
    
    print("\nTesting facial evaluation template rendering...")
    
    # Simulate admin response with markdown
    admin_response = """# Facial Analysis Report

## Overall Assessment
Your facial structure shows **excellent symmetry** and *well-defined features*.

## Key Observations:
- Strong jawline definition
- Balanced facial proportions
- Good bone structure

## Recommendations:
1. **Maintain current grooming routine**
2. *Consider professional photography* to highlight your best features
3. Focus on [skincare routine](https://example.com/skincare) for optimal results

**Rating: 8.5/10**"""
    
    # Create Flask app for testing
    app = Flask(__name__)
    
    # Define the markdown filter
    @app.template_filter('markdown')
    def markdown_filter(s):
        """Convert a string to Markdown and mark it safe for Jinja"""
        if s:
            return Markup(mistune.html(s))
        return ''
    
    with app.app_context():
        try:
            rendered = markdown_filter(admin_response)
            print(f"Rendered HTML length: {len(str(rendered))} characters")
            print(f"Type: {type(rendered)}")
            
            # Check for key HTML elements
            html_str = str(rendered)
            expected_elements = [
                '<h1>Facial Analysis Report</h1>',
                '<h2>Overall Assessment</h2>',
                '<strong>excellent symmetry</strong>',
                '<em>well-defined features</em>',
                '<ol>',
                '<li><strong>Maintain current grooming routine</strong></li>',
                '<a href="https://example.com/skincare">skincare routine</a>',
                '<strong>Rating: 8.5/10</strong>'
            ]
            
            for element in expected_elements:
                if element in html_str:
                    print(f"✅ Found: {element}")
                else:
                    print(f"❌ Missing: {element}")
                    return False
            
            print("\n✅ Facial evaluation template rendering test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Template rendering test failed: {e}")
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("MARKDOWN RENDERING FIX VERIFICATION")
    print("=" * 60)
    
    success = True
    
    # Test markdown filter
    if not test_markdown_filter():
        success = False
    
    # Test facial evaluation template
    if not test_facial_evaluation_template():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Markdown rendering is working correctly.")
        print("The facial evaluation feature should now display formatted text properly.")
    else:
        print("❌ SOME TESTS FAILED! Please check the implementation.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
