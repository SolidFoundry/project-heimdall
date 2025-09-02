#!/usr/bin/env python
"""
Simple security check script
Check for hardcoded sensitive information in the project
"""

import os
import re
import sys
from pathlib import Path

def main():
    """Main function"""
    print("Project Heimdall Security Check\n")
    print("=" * 50)
    print()
    
    project_root = Path(__file__).parent
    print(f"Scanning directory: {project_root}")
    print()
    
    # Patterns to check
    patterns = [
        (r'api[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', "API Key"),
        (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API Key"),
        (r'password\s*[:=]\s*["\']?[^"\'\s]{6,}', "Password"),
        (r'secret[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9+/=]{20,}', "Secret Key"),
        (r'postgres://[^:@]+:[^@]+@', "PostgreSQL Connection String"),
        (r'-----BEGIN.*PRIVATE KEY-----', "Private Key"),
    ]
    
    # Files to check
    extensions = ['.py', '.js', '.json', '.yaml', '.yml', '.toml', '.ini']
    secrets_found = []
    
    # Scan files
    for root, dirs, files in os.walk(project_root):
        # Skip directories
        skip_dirs = ['.git', '.venv', 'venv', 'env', '__pycache__', 'node_modules']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = Path(root) / file
                
                # Skip .env files
                if file.startswith('.env'):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern, description in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            secrets_found.append((file_path.relative_to(project_root), line_num, description))
                
                except Exception:
                    pass
    
    # Report results
    if not secrets_found:
        print("OK: No hardcoded sensitive information found")
        print("\nRecommendations:")
        print("1. Use environment variables for all sensitive data")
        print("2. Keep .env in .gitignore")
        print("3. Run this check regularly")
    else:
        print(f"WARNING: Found {len(secrets_found)} potential issues:\n")
        
        for file_path, line_num, description in secrets_found:
            print(f"File: {file_path}")
            print(f"  Line {line_num}: {description}")
            print()
        
        print("\nPlease remove hardcoded sensitive information!")
        sys.exit(1)

if __name__ == "__main__":
    main()