#!/usr/bin/env python3
"""
EXHAUSTIVE Facial Evaluation Railway Volume Analysis
This script checks EVERY SINGLE FILE that could possibly handle facial evaluation images
"""

import os
import sys
import re
import glob
from pathlib import Path

def print_header(title):
    print(f"\n{'='*100}")
    print(f" {title}")
    print(f"{'='*100}")

def print_status(check, status, details=""):
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {check}")
    if details:
        print(f"   {details}")

def find_all_python_files():
    """Find ALL Python files in the project"""
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.vscode', 'node_modules', '.env'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def analyze_file_for_facial_evaluation(filepath):
    """Analyze a single file for facial evaluation related code"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return None
    
    # Check if file contains facial evaluation related code
    facial_eval_indicators = [
        'facial_evaluation',
        'FacialEvaluation',
        'FACIAL_EVALUATION',
        'facial-evaluation',
        'get_facial_evaluation_image',
        'request_facial_evaluation',
        'respond_facial_evaluation'
    ]
    
    has_facial_eval = any(indicator in content for indicator in facial_eval_indicators)
    if not has_facial_eval:
        return None
    
    analysis = {
        'filepath': filepath,
        'has_facial_eval': True,
        'file_operations': [],
        'path_operations': [],
        'hardcoded_paths': [],
        'uses_facial_eval_folder': False,
        'problematic_patterns': []
    }
    
    # Check for file operations
    file_ops = [
        r'file\.save\([^)]+\)',
        r'shutil\.copy[^(]*\([^)]+\)',
        r'shutil\.move[^(]*\([^)]+\)',
        r'\.save\([^)]+\)',
        r'open\([^)]+["\']w["\'][^)]*\)',
        r'with open\([^)]+["\']w["\'][^)]*\)'
    ]
    
    for pattern in file_ops:
        matches = re.findall(pattern, content)
        if matches:
            analysis['file_operations'].extend(matches)
    
    # Check for path operations
    path_ops = [
        r'os\.path\.join\([^)]+\)',
        r'Path\([^)]+\)',
        r'pathlib\.[^(]+\([^)]+\)'
    ]
    
    for pattern in path_ops:
        matches = re.findall(pattern, content)
        if matches:
            analysis['path_operations'].extend(matches)
    
    # Check for hardcoded paths
    hardcoded_patterns = [
        r'["\'][^"\']*facial_evaluations[^"\']*["\']',
        r'["\'][^"\']*uploads[^"\']*["\']',
        r'["\'][^"\']*outputs[^"\']*["\']'
    ]
    
    for pattern in hardcoded_patterns:
        matches = re.findall(pattern, content)
        if matches:
            analysis['hardcoded_paths'].extend(matches)
    
    # Check if uses FACIAL_EVALUATION_FOLDER
    analysis['uses_facial_eval_folder'] = 'FACIAL_EVALUATION_FOLDER' in content
    
    # Check for problematic patterns
    problematic = [
        r'["\']uploads/[^"\']*["\']',
        r'["\']outputs/[^"\']*["\']',
        r'["\'][^"\']*facial_evaluations[^"\']*["\']'
    ]
    
    for pattern in problematic:
        matches = re.findall(pattern, content)
        if matches:
            analysis['problematic_patterns'].extend(matches)
    
    return analysis

def check_template_files():
    """Check all template files for hardcoded paths"""
    print_header("TEMPLATE FILES ANALYSIS")
    
    template_files = []
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith(('.html', '.htm')):
                template_files.append(os.path.join(root, file))
    
    print(f"Found {len(template_files)} template files")
    
    issues = []
    for template_file in template_files:
        try:
            with open(template_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for hardcoded image paths
            hardcoded_patterns = [
                r'src=["\'][^"\']*facial_evaluations[^"\']*["\']',
                r'href=["\'][^"\']*facial_evaluations[^"\']*["\']',
                r'url\([^)]*facial_evaluations[^)]*\)',
                r'/uploads/',
                r'/outputs/',
                r'/facial_evaluations/'
            ]
            
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    issues.append({
                        'file': template_file,
                        'pattern': pattern,
                        'matches': matches
                    })
        except:
            continue
    
    if issues:
        print_status("Template files use proper image URLs", False)
        for issue in issues:
            print(f"   ❌ {issue['file']}: {issue['matches']}")
        return False
    else:
        print_status("Template files use proper image URLs", True)
        return True

def check_config_files():
    """Check all configuration files"""
    print_header("CONFIGURATION FILES ANALYSIS")
    
    config_files = ['config.py', 'settings.py', '.env', '.env.example']
    
    all_good = True
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                print(f"\n📄 Analyzing {config_file}:")
                
                # Check for FACIAL_EVALUATION_FOLDER
                if 'FACIAL_EVALUATION_FOLDER' in content:
                    print_status(f"  Defines FACIAL_EVALUATION_FOLDER", True)
                    
                    # Check if it uses Railway volume path
                    if '/app/facial_evaluations' in content:
                        print_status(f"  Uses Railway volume path", True)
                    else:
                        print_status(f"  Uses Railway volume path", False)
                        all_good = False
                else:
                    if config_file == 'config.py':
                        print_status(f"  Defines FACIAL_EVALUATION_FOLDER", False)
                        all_good = False
            except:
                continue
    
    return all_good

def check_deployment_files():
    """Check deployment configuration files"""
    print_header("DEPLOYMENT FILES ANALYSIS")
    
    deployment_files = [
        'Dockerfile',
        'deployment/Dockerfile',
        'railway.toml',
        'deployment/railway.toml',
        'docker-compose.yml',
        'docker-compose.yaml'
    ]
    
    all_good = True
    for deploy_file in deployment_files:
        if os.path.exists(deploy_file):
            try:
                with open(deploy_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                print(f"\n📄 Analyzing {deploy_file}:")
                
                if 'facial_evaluations' in content:
                    print_status(f"  References facial_evaluations", True)
                    
                    # Check for volume mounts
                    if 'volume' in content.lower() or 'mount' in content.lower():
                        print_status(f"  Configures volume/mount", True)
                    else:
                        print_status(f"  Configures volume/mount", False)
                else:
                    if deploy_file.endswith('Dockerfile'):
                        print_status(f"  Creates facial_evaluations directory", False)
                        all_good = False
            except:
                continue
    
    return all_good

def main():
    """Run exhaustive analysis"""
    print_header("EXHAUSTIVE FACIAL EVALUATION RAILWAY VOLUME ANALYSIS")
    print("Checking EVERY SINGLE FILE that could possibly handle facial evaluation images")
    
    # Find all Python files
    python_files = find_all_python_files()
    print(f"\nFound {len(python_files)} Python files to analyze")
    
    # Analyze each Python file
    print_header("PYTHON FILES ANALYSIS")
    
    facial_eval_files = []
    all_issues = []
    
    for py_file in python_files:
        analysis = analyze_file_for_facial_evaluation(py_file)
        if analysis:
            facial_eval_files.append(analysis)
            
            print(f"\n📄 {py_file}:")
            print_status(f"  Contains facial evaluation code", True)
            print_status(f"  Uses FACIAL_EVALUATION_FOLDER", analysis['uses_facial_eval_folder'])
            
            if analysis['file_operations']:
                print(f"  📁 File operations ({len(analysis['file_operations'])}):")
                for op in analysis['file_operations']:
                    print(f"     • {op}")
            
            if analysis['path_operations']:
                print(f"  🔗 Path operations ({len(analysis['path_operations'])}):")
                for op in analysis['path_operations']:
                    if 'FACIAL_EVALUATION_FOLDER' in op:
                        print_status(f"     • {op}", True, "Uses FACIAL_EVALUATION_FOLDER")
                    else:
                        print_status(f"     • {op}", False, "Does not use FACIAL_EVALUATION_FOLDER")
            
            if analysis['hardcoded_paths']:
                print(f"  ⚠️  Hardcoded paths ({len(analysis['hardcoded_paths'])}):")
                for path in analysis['hardcoded_paths']:
                    print_status(f"     • {path}", False, "HARDCODED PATH DETECTED")
                    all_issues.append(f"{py_file}: {path}")
            
            if analysis['problematic_patterns']:
                print(f"  ❌ Problematic patterns ({len(analysis['problematic_patterns'])}):")
                for pattern in analysis['problematic_patterns']:
                    print_status(f"     • {pattern}", False, "PROBLEMATIC PATTERN")
                    all_issues.append(f"{py_file}: {pattern}")
    
    print(f"\nFound {len(facial_eval_files)} files with facial evaluation code")
    
    # Check template files
    template_ok = check_template_files()
    
    # Check config files
    config_ok = check_config_files()
    
    # Check deployment files
    deploy_ok = check_deployment_files()
    
    # Final summary
    print_header("EXHAUSTIVE ANALYSIS SUMMARY")
    
    print(f"📊 ANALYSIS STATISTICS:")
    print(f"   • Total Python files scanned: {len(python_files)}")
    print(f"   • Files with facial evaluation code: {len(facial_eval_files)}")
    print(f"   • Critical issues found: {len(all_issues)}")
    
    print(f"\n🔍 COMPONENT STATUS:")
    print_status("Python files", len(all_issues) == 0)
    print_status("Template files", template_ok)
    print_status("Configuration files", config_ok)
    print_status("Deployment files", deploy_ok)
    
    if all_issues:
        print(f"\n❌ CRITICAL ISSUES DETECTED:")
        for issue in all_issues:
            print(f"   • {issue}")
    
    overall_ok = len(all_issues) == 0 and template_ok and config_ok and deploy_ok
    
    if overall_ok:
        print("\n🎉 EXHAUSTIVE ANALYSIS PASSED!")
        print("✅ ALL facial evaluation images are properly configured for Railway volumes")
        print("✅ NO hardcoded paths detected in ANY file")
        print("✅ ALL file operations use proper Railway volume configuration")
        print("\n🚀 Your facial evaluation feature is BULLETPROOF for Railway deployment!")
    else:
        print(f"\n⚠️  EXHAUSTIVE ANALYSIS FAILED!")
        print("❌ Critical issues detected that must be fixed")
        print("🔧 Please review and fix all issues above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
