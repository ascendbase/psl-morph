"""
Fix Railway Deployment Panic Issue
Addresses the Docker build panic during deployment
"""

import os
import subprocess
import time

def fix_railway_deployment():
    """Fix Railway deployment panic issue"""
    print("Fixing Railway Deployment Panic Issue")
    print("=" * 50)
    
    # Step 1: Check if we have a .dockerignore to reduce build context
    dockerignore_content = """
# Ignore unnecessary files to reduce build context
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/
.DS_Store
*.swp
*.swo
*~
.vscode/
.idea/
*.md
test_*.py
debug_*.py
fix_*.py
verify_*.py
setup_*.py
*.bat
*.sh
cloudflared.log*
outputs/
uploads/
instance/
facial_evaluations/
"""
    
    # Create .dockerignore if it doesn't exist
    if not os.path.exists('.dockerignore'):
        with open('.dockerignore', 'w') as f:
            f.write(dockerignore_content)
        print("✅ Created .dockerignore to reduce build context")
    else:
        print("✅ .dockerignore already exists")
    
    # Step 2: Check Dockerfile for optimization
    dockerfile_optimized = """FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs instance

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
"""
    
    # Check if Dockerfile needs optimization
    if os.path.exists('Dockerfile'):
        with open('Dockerfile', 'r') as f:
            current_dockerfile = f.read()
        
        if 'EXPOSE 8080' not in current_dockerfile:
            with open('Dockerfile', 'w') as f:
                f.write(dockerfile_optimized)
            print("✅ Optimized Dockerfile for Railway deployment")
        else:
            print("✅ Dockerfile already optimized")
    else:
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_optimized)
        print("✅ Created optimized Dockerfile")
    
    # Step 3: Check railway.toml configuration
    railway_config = """[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
"""
    
    if not os.path.exists('railway.toml'):
        with open('railway.toml', 'w') as f:
            f.write(railway_config)
        print("✅ Created railway.toml configuration")
    else:
        print("✅ railway.toml already exists")
    
    # Step 4: Clean up any large files that might cause build issues
    large_files_to_remove = [
        'cloudflared.log',
        'cloudflared.log.1',
        'cloudflared.log.2'
    ]
    
    for file in large_files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removed large file: {file}")
    
    print("\n" + "=" * 50)
    print("🔧 RAILWAY DEPLOYMENT FIX APPLIED!")
    print("\n📋 What was fixed:")
    print("   • Created/optimized .dockerignore to reduce build context")
    print("   • Optimized Dockerfile for Railway deployment")
    print("   • Added railway.toml configuration")
    print("   • Cleaned up large log files")
    print("\n🚀 Next steps:")
    print("   1. Commit these changes to git")
    print("   2. Push to Railway for redeployment")
    print("   3. The panic issue should be resolved")
    
    return True

if __name__ == "__main__":
    fix_railway_deployment()
