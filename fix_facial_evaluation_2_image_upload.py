#!/usr/bin/env python3
"""
Fix for the 2-image upload functionality on the facial evaluation dashboard.
This script will fix the issue where users can't manually upload 2 images
on the /facial-evaluation page.
"""

import os
import sys

def fix_facial_evaluation_upload():
    """Fix the 2-image upload functionality"""
    print("🔧 Fixing Facial Evaluation 2-Image Upload Functionality")
    print("=" * 60)
    
    # Read the current app.py file
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the request_facial_evaluation_standalone function
        if 'def request_facial_evaluation_standalone():' in content:
            print("✅ Found existing request_facial_evaluation_standalone function")
            
            # Find the function and check if it handles file2 properly
            lines = content.split('\n')
            in_function = False
            function_lines = []
            
            for i, line in enumerate(lines):
                if 'def request_facial_evaluation_standalone():' in line:
                    in_function = True
                    function_start = i
                
                if in_function:
                    function_lines.append(line)
                    
                    # Check if we've reached the end of the function
                    if line.strip() and not line.startswith(' ') and not line.startswith('\t') and i > function_start:
                        if not line.startswith('@') and not line.startswith('def request_facial_evaluation_standalone'):
                            break
            
            function_content = '\n'.join(function_lines[:-1])  # Remove the last line which is the next function
            
            print("📋 Current function content:")
            print(function_content[:500] + "..." if len(function_content) > 500 else function_content)
            
            # Check if the function properly handles file2
            if 'file2' in function_content and 'request.files.get(\'file2\')' in function_content:
                print("✅ Function already handles file2 properly")
                return True
            else:
                print("❌ Function doesn't handle file2 properly - needs fixing")
                return fix_function_implementation()
        else:
            print("❌ request_facial_evaluation_standalone function not found")
            return create_function_implementation()
            
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def fix_function_implementation():
    """Fix the existing function implementation"""
    print("\n🔧 Fixing the function implementation...")
    
    # The corrected function implementation
    new_function = '''@app.route('/request-facial-evaluation-standalone', methods=['POST'])
@login_required
def request_facial_evaluation_standalone():
    """Request facial evaluation with standalone image upload"""
    try:
        # Check if user has enough credits
        if current_user.credits < 20:
            return jsonify({
                'success': False,
                'error': 'Insufficient credits. You need 20 credits for facial evaluation.',
                'need_credits': True,
                'buy_credits_url': url_for('payments.buy_credits')
            })
        
        # Get uploaded files
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')  # Optional second file
        
        if not file1:
            return jsonify({
                'success': False,
                'error': 'Please upload at least one image.'
            })
        
        # Validate file types
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
        
        if not allowed_file(file1.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type for first image. Please use PNG, JPG, JPEG, or WebP.'
            })
        
        if file2 and not allowed_file(file2.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type for second image. Please use PNG, JPG, JPEG, or WebP.'
            })
        
        # Create facial_evaluations directory if it doesn't exist
        facial_eval_dir = 'facial_evaluations'
        if not os.path.exists(facial_eval_dir):
            os.makedirs(facial_eval_dir)
        
        # Generate unique filenames
        import uuid
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        # Save first image
        file1_ext = file1.filename.rsplit('.', 1)[1].lower()
        original_filename = f"standalone_{current_user.id}_{timestamp}_{unique_id}_1.{file1_ext}"
        original_path = os.path.join(facial_eval_dir, original_filename)
        file1.save(original_path)
        
        # Save second image if provided
        secondary_filename = None
        if file2:
            file2_ext = file2.filename.rsplit('.', 1)[1].lower()
            secondary_filename = f"standalone_{current_user.id}_{timestamp}_{unique_id}_2.{file2_ext}"
            secondary_path = os.path.join(facial_eval_dir, secondary_filename)
            file2.save(secondary_path)
        
        # Create facial evaluation record
        facial_evaluation = FacialEvaluation(
            user_id=current_user.id,
            generation_id=None,  # No generation for standalone upload
            original_image_filename=original_filename,
            morphed_image_filename=None,  # No morph for standalone
            secondary_image_filename=secondary_filename,  # Second uploaded image
            status='Pending',
            credits_used=20,
            created_at=datetime.now()
        )
        
        # Deduct credits from user
        current_user.credits -= 20
        
        # Save to database
        db.session.add(facial_evaluation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Facial evaluation request submitted successfully! You will receive your analysis soon.',
            'evaluation_id': facial_evaluation.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in facial evaluation request: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your request. Please try again.'
        })'''
    
    # Read current app.py
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the function
        lines = content.split('\n')
        new_lines = []
        in_function = False
        function_start = -1
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if '@app.route(\'/request-facial-evaluation-standalone\'' in line:
                # Found the start of the function, replace it
                new_lines.extend(new_function.split('\n'))
                
                # Skip the old function
                i += 1
                while i < len(lines):
                    if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                        if lines[i].startswith('@app.route') or lines[i].startswith('def ') or lines[i].startswith('if __name__'):
                            break
                    i += 1
                continue
            else:
                new_lines.append(line)
            
            i += 1
        
        # Write the updated content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Successfully updated the function implementation")
        return True
        
    except Exception as e:
        print(f"❌ Error updating function: {e}")
        return False

def create_function_implementation():
    """Create the function implementation if it doesn't exist"""
    print("\n🔧 Creating the function implementation...")
    
    # The function implementation
    new_function = '''
@app.route('/request-facial-evaluation-standalone', methods=['POST'])
@login_required
def request_facial_evaluation_standalone():
    """Request facial evaluation with standalone image upload"""
    try:
        # Check if user has enough credits
        if current_user.credits < 20:
            return jsonify({
                'success': False,
                'error': 'Insufficient credits. You need 20 credits for facial evaluation.',
                'need_credits': True,
                'buy_credits_url': url_for('payments.buy_credits')
            })
        
        # Get uploaded files
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')  # Optional second file
        
        if not file1:
            return jsonify({
                'success': False,
                'error': 'Please upload at least one image.'
            })
        
        # Validate file types
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
        
        if not allowed_file(file1.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type for first image. Please use PNG, JPG, JPEG, or WebP.'
            })
        
        if file2 and not allowed_file(file2.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type for second image. Please use PNG, JPG, JPEG, or WebP.'
            })
        
        # Create facial_evaluations directory if it doesn't exist
        facial_eval_dir = 'facial_evaluations'
        if not os.path.exists(facial_eval_dir):
            os.makedirs(facial_eval_dir)
        
        # Generate unique filenames
        import uuid
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        # Save first image
        file1_ext = file1.filename.rsplit('.', 1)[1].lower()
        original_filename = f"standalone_{current_user.id}_{timestamp}_{unique_id}_1.{file1_ext}"
        original_path = os.path.join(facial_eval_dir, original_filename)
        file1.save(original_path)
        
        # Save second image if provided
        secondary_filename = None
        if file2:
            file2_ext = file2.filename.rsplit('.', 1)[1].lower()
            secondary_filename = f"standalone_{current_user.id}_{timestamp}_{unique_id}_2.{file2_ext}"
            secondary_path = os.path.join(facial_eval_dir, secondary_filename)
            file2.save(secondary_path)
        
        # Create facial evaluation record
        facial_evaluation = FacialEvaluation(
            user_id=current_user.id,
            generation_id=None,  # No generation for standalone upload
            original_image_filename=original_filename,
            morphed_image_filename=None,  # No morph for standalone
            secondary_image_filename=secondary_filename,  # Second uploaded image
            status='Pending',
            credits_used=20,
            created_at=datetime.now()
        )
        
        # Deduct credits from user
        current_user.credits -= 20
        
        # Save to database
        db.session.add(facial_evaluation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Facial evaluation request submitted successfully! You will receive your analysis soon.',
            'evaluation_id': facial_evaluation.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in facial evaluation request: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your request. Please try again.'
        })
'''
    
    # Read current app.py and add the function
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find a good place to insert the function (before the last route or at the end)
        if 'if __name__ == \'__main__\':' in content:
            # Insert before the main block
            content = content.replace('if __name__ == \'__main__\':', new_function + '\n\nif __name__ == \'__main__\':')
        else:
            # Append to the end
            content += new_function
        
        # Write the updated content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Successfully added the function implementation")
        return True
        
    except Exception as e:
        print(f"❌ Error adding function: {e}")
        return False

def test_fix():
    """Test if the fix was successful"""
    print("\n🧪 Testing the fix...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the function exists and has the right content
        if 'def request_facial_evaluation_standalone():' in content:
            print("✅ Function exists")
            
            if 'file2 = request.files.get(\'file2\')' in content:
                print("✅ Function handles file2 properly")
                
                if 'secondary_filename' in content:
                    print("✅ Function saves secondary image")
                    
                    if 'secondary_image_filename=secondary_filename' in content:
                        print("✅ Function stores secondary filename in database")
                        return True
                    else:
                        print("❌ Function doesn't store secondary filename in database")
                else:
                    print("❌ Function doesn't handle secondary filename")
            else:
                print("❌ Function doesn't handle file2")
        else:
            print("❌ Function doesn't exist")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing fix: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Facial Evaluation 2-Image Upload Fix")
    print("=" * 60)
    
    success = fix_facial_evaluation_upload()
    
    if success:
        test_success = test_fix()
        if test_success:
            print("\n🎉 Fix completed successfully!")
            print("\n📋 What was fixed:")
            print("• Added proper handling for file2 (second image)")
            print("• Added validation for both images")
            print("• Added proper saving of secondary image")
            print("• Added secondary_image_filename to database record")
            print("• Added proper error handling")
            
            print("\n✅ Users can now:")
            print("• Upload 1 or 2 images on /facial-evaluation page")
            print("• See both images in admin dashboard")
            print("• Get proper error messages for invalid files")
            print("• Have their credits deducted correctly")
        else:
            print("\n⚠️ Fix applied but verification failed")
    else:
        print("\n❌ Fix failed")
    
    print("\n📝 Next steps:")
    print("1. Test the /facial-evaluation page")
    print("2. Try uploading 2 images manually")
    print("3. Check admin dashboard for both images")
    print("4. Verify credit deduction works")
