#!/usr/bin/env python3
"""
Debug script to check facial evaluation image serving
"""

import os
import sys
from models import db, FacialEvaluation, init_db
from config import *

def debug_facial_evaluation_image(evaluation_id):
    """Debug facial evaluation image serving"""
    
    print(f"🔍 Debugging facial evaluation image: {evaluation_id}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📁 Output folder: {OUTPUT_FOLDER}")
    
    # Check if evaluation exists
    evaluation = FacialEvaluation.query.get(evaluation_id)
    if not evaluation:
        print(f"❌ Evaluation {evaluation_id} not found in database")
        return
    
    print(f"✅ Evaluation found:")
    print(f"   - User ID: {evaluation.user_id}")
    print(f"   - Status: {evaluation.status}")
    print(f"   - Original image: {evaluation.original_image_filename}")
    print(f"   - Morphed image: {evaluation.morphed_image_filename}")
    print(f"   - Generation ID: {evaluation.generation_id}")
    
    # Check original image file
    if evaluation.original_image_filename:
        original_path = os.path.join(UPLOAD_FOLDER, evaluation.original_image_filename)
        print(f"\n📸 Original image check:")
        print(f"   - Filename: {evaluation.original_image_filename}")
        print(f"   - Expected path: {original_path}")
        print(f"   - File exists: {os.path.exists(original_path)}")
        
        if os.path.exists(original_path):
            file_size = os.path.getsize(original_path)
            print(f"   - File size: {file_size} bytes")
        else:
            print(f"   ❌ File not found!")
            
            # List files in upload folder
            print(f"\n📂 Files in upload folder:")
            try:
                files = os.listdir(UPLOAD_FOLDER)
                for file in files[:10]:  # Show first 10 files
                    print(f"   - {file}")
                if len(files) > 10:
                    print(f"   ... and {len(files) - 10} more files")
            except Exception as e:
                print(f"   ❌ Error listing files: {e}")
    else:
        print(f"\n📸 No original image filename in database")
    
    # Check morphed image file
    if evaluation.morphed_image_filename:
        morphed_path = os.path.join(OUTPUT_FOLDER, evaluation.morphed_image_filename)
        print(f"\n🎭 Morphed image check:")
        print(f"   - Filename: {evaluation.morphed_image_filename}")
        print(f"   - Expected path: {morphed_path}")
        print(f"   - File exists: {os.path.exists(morphed_path)}")
        
        if os.path.exists(morphed_path):
            file_size = os.path.getsize(morphed_path)
            print(f"   - File size: {file_size} bytes")
        else:
            print(f"   ❌ File not found!")
            
            # List files in output folder
            print(f"\n📂 Files in output folder:")
            try:
                files = os.listdir(OUTPUT_FOLDER)
                for file in files[:10]:  # Show first 10 files
                    print(f"   - {file}")
                if len(files) > 10:
                    print(f"   ... and {len(files) - 10} more files")
            except Exception as e:
                print(f"   ❌ Error listing files: {e}")
    else:
        print(f"\n🎭 No morphed image filename in database")
    
    # Check if linked to generation
    if evaluation.generation_id:
        from models import Generation
        generation = Generation.query.get(evaluation.generation_id)
        if generation:
            print(f"\n🔗 Linked generation found:")
            print(f"   - Input filename: {generation.input_filename}")
            print(f"   - Output filename: {generation.output_filename}")
            print(f"   - Status: {generation.status}")
            
            # Check if generation files exist
            if generation.input_filename:
                gen_input_path = os.path.join(UPLOAD_FOLDER, generation.input_filename)
                print(f"   - Input file exists: {os.path.exists(gen_input_path)}")
            
            if generation.output_filename:
                gen_output_path = os.path.join(OUTPUT_FOLDER, generation.output_filename)
                print(f"   - Output file exists: {os.path.exists(gen_output_path)}")
        else:
            print(f"\n❌ Linked generation {evaluation.generation_id} not found")

if __name__ == "__main__":
    # Initialize Flask app context
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        init_db(app)
        
        # Debug the specific evaluation ID from the error
        evaluation_id = "aa39d89a-e8af-4d1c-b551-dfa1a8b8b346"
        debug_facial_evaluation_image(evaluation_id)
