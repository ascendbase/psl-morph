#!/usr/bin/env python3
"""
Railway Volume Image Deletion Utility

This script provides functionality to delete images from Railway volume storage.
It can be used to clean up old facial evaluation images and manage storage space.
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import FacialEvaluation, Generation
from config import Config

def get_volume_path():
    """Get the Railway volume path for facial evaluations"""
    if os.path.exists('/app/facial_evaluations'):
        return '/app/facial_evaluations'
    elif os.path.exists('./facial_evaluations'):
        return './facial_evaluations'
    else:
        print("❌ Facial evaluations volume not found!")
        return None

def list_all_images():
    """List all images in the volume"""
    volume_path = get_volume_path()
    if not volume_path:
        return []
    
    images = []
    for root, dirs, files in os.walk(volume_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                full_path = os.path.join(root, file)
                stat = os.stat(full_path)
                images.append({
                    'path': full_path,
                    'name': file,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
    
    return sorted(images, key=lambda x: x['modified'], reverse=True)

def list_orphaned_images():
    """List images that are not referenced in the database"""
    with app.app_context():
        volume_path = get_volume_path()
        if not volume_path:
            return []
        
        # Get all image files
        all_images = list_all_images()
        
        # Get all referenced images from database
        referenced_images = set()
        
        # Check facial evaluations
        evaluations = FacialEvaluation.query.all()
        for eval in evaluations:
            if eval.image_path:
                referenced_images.add(os.path.basename(eval.image_path))
            if eval.secondary_image_path:
                referenced_images.add(os.path.basename(eval.secondary_image_path))
        
        # Check generations (if they use volume storage)
        generations = Generation.query.all()
        for gen in generations:
            if gen.input_image_path and 'facial_evaluations' in gen.input_image_path:
                referenced_images.add(os.path.basename(gen.input_image_path))
            if gen.output_image_path and 'facial_evaluations' in gen.output_image_path:
                referenced_images.add(os.path.basename(gen.output_image_path))
        
        # Find orphaned images
        orphaned = []
        for image in all_images:
            if image['name'] not in referenced_images:
                orphaned.append(image)
        
        return orphaned

def list_old_images(days=30):
    """List images older than specified days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    all_images = list_all_images()
    
    old_images = []
    for image in all_images:
        if image['modified'] < cutoff_date:
            old_images.append(image)
    
    return old_images

def delete_image(image_path):
    """Delete a single image file"""
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            return True
        else:
            print(f"⚠️ Image not found: {image_path}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {image_path}: {e}")
        return False

def delete_images(image_list, confirm=True):
    """Delete multiple images with optional confirmation"""
    if not image_list:
        print("📭 No images to delete.")
        return 0
    
    total_size = sum(img['size'] for img in image_list)
    print(f"\n📊 Found {len(image_list)} images to delete")
    print(f"💾 Total size: {format_size(total_size)}")
    
    if confirm:
        print("\n📋 Images to be deleted:")
        for i, img in enumerate(image_list[:10]):  # Show first 10
            print(f"  {i+1}. {img['name']} ({format_size(img['size'])}) - {img['modified'].strftime('%Y-%m-%d %H:%M')}")
        
        if len(image_list) > 10:
            print(f"  ... and {len(image_list) - 10} more images")
        
        response = input(f"\n❓ Are you sure you want to delete {len(image_list)} images? (yes/no): ").lower()
        if response not in ['yes', 'y']:
            print("❌ Deletion cancelled.")
            return 0
    
    deleted_count = 0
    for img in image_list:
        if delete_image(img['path']):
            deleted_count += 1
            print(f"✅ Deleted: {img['name']}")
        else:
            print(f"❌ Failed to delete: {img['name']}")
    
    print(f"\n🎉 Successfully deleted {deleted_count} out of {len(image_list)} images")
    return deleted_count

def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_storage_stats():
    """Get storage statistics"""
    volume_path = get_volume_path()
    if not volume_path:
        return None
    
    total_size = 0
    total_files = 0
    
    for root, dirs, files in os.walk(volume_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                total_files += 1
    
    return {
        'total_files': total_files,
        'total_size': total_size,
        'volume_path': volume_path
    }

def main():
    """Main function with interactive menu"""
    print("🗂️ Railway Volume Image Management Tool")
    print("=" * 50)
    
    stats = get_storage_stats()
    if not stats:
        print("❌ Cannot access volume storage!")
        return
    
    print(f"📁 Volume path: {stats['volume_path']}")
    print(f"📊 Total images: {stats['total_files']}")
    print(f"💾 Total size: {format_size(stats['total_size'])}")
    print()
    
    while True:
        print("\n🔧 Available Actions:")
        print("1. 📋 List all images")
        print("2. 🧹 List orphaned images (not in database)")
        print("3. ⏰ List old images (older than X days)")
        print("4. 🗑️ Delete orphaned images")
        print("5. 🗑️ Delete old images")
        print("6. 📊 Show storage statistics")
        print("7. 🚪 Exit")
        
        choice = input("\n❓ Choose an action (1-7): ").strip()
        
        if choice == '1':
            images = list_all_images()
            print(f"\n📋 All Images ({len(images)} total):")
            for i, img in enumerate(images[:20]):  # Show first 20
                print(f"  {i+1}. {img['name']} ({format_size(img['size'])}) - {img['modified'].strftime('%Y-%m-%d %H:%M')}")
            if len(images) > 20:
                print(f"  ... and {len(images) - 20} more images")
        
        elif choice == '2':
            orphaned = list_orphaned_images()
            print(f"\n🧹 Orphaned Images ({len(orphaned)} total):")
            for i, img in enumerate(orphaned[:20]):
                print(f"  {i+1}. {img['name']} ({format_size(img['size'])}) - {img['modified'].strftime('%Y-%m-%d %H:%M')}")
            if len(orphaned) > 20:
                print(f"  ... and {len(orphaned) - 20} more images")
        
        elif choice == '3':
            days = input("📅 Enter number of days (default 30): ").strip()
            try:
                days = int(days) if days else 30
            except ValueError:
                days = 30
            
            old_images = list_old_images(days)
            print(f"\n⏰ Images older than {days} days ({len(old_images)} total):")
            for i, img in enumerate(old_images[:20]):
                print(f"  {i+1}. {img['name']} ({format_size(img['size'])}) - {img['modified'].strftime('%Y-%m-%d %H:%M')}")
            if len(old_images) > 20:
                print(f"  ... and {len(old_images) - 20} more images")
        
        elif choice == '4':
            orphaned = list_orphaned_images()
            delete_images(orphaned)
        
        elif choice == '5':
            days = input("📅 Enter number of days (default 30): ").strip()
            try:
                days = int(days) if days else 30
            except ValueError:
                days = 30
            
            old_images = list_old_images(days)
            delete_images(old_images)
        
        elif choice == '6':
            stats = get_storage_stats()
            print(f"\n📊 Storage Statistics:")
            print(f"📁 Volume path: {stats['volume_path']}")
            print(f"📊 Total images: {stats['total_files']}")
            print(f"💾 Total size: {format_size(stats['total_size'])}")
            
            # Show breakdown by type
            all_images = list_all_images()
            if all_images:
                newest = max(all_images, key=lambda x: x['modified'])
                oldest = min(all_images, key=lambda x: x['modified'])
                print(f"📅 Newest image: {newest['modified'].strftime('%Y-%m-%d %H:%M')}")
                print(f"📅 Oldest image: {oldest['modified'].strftime('%Y-%m-%d %H:%M')}")
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
