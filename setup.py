#!/usr/bin/env python3
"""
Setup script for Task Management API
This script automates the local development environment setup
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, shell=False):
    """Execute a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version():
    """Check if Python version is 3.11 or higher"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"✗ Python 3.11+ required. Current version: {version.major}.{version.minor}.{version.micro}")
        return False

def create_virtual_environment():
    """Create a virtual environment"""
    print("\n📦 Creating virtual environment...")
    
    # Check if venv already exists
    if os.path.exists("venv"):
        print("⚠️  Virtual environment already exists. Skipping creation.")
        return True
    
    # Create virtual environment
    success, output = run_command([sys.executable, "-m", "venv", "venv"])
    if success:
        print("✓ Virtual environment created successfully")
        return True
    else:
        print(f"✗ Failed to create virtual environment: {output}")
        return False

def get_activation_command():
    """Get the correct activation command based on OS"""
    system = platform.system().lower()
    if system == "windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies in virtual environment"""
    print("\n📚 Installing dependencies...")
    
    # Get the correct pip path based on OS
    system = platform.system().lower()
    if system == "windows":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    # Upgrade pip first
    success, output = run_command([pip_path, "install", "--upgrade", "pip"])
    if not success:
        print(f"⚠️  Warning: Could not upgrade pip: {output}")
    
    # Install requirements
    success, output = run_command([pip_path, "install", "-r", "requirements.txt"])
    if success:
        print("✓ Dependencies installed successfully")
        return True
    else:
        print(f"✗ Failed to install dependencies: {output}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n⚙️  Setting up environment configuration...")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists. Skipping creation.")
        return True
    
    if os.path.exists(".env.example"):
        try:
            with open(".env.example", "r") as source:
                content = source.read()
            
            with open(".env", "w") as target:
                target.write(content)
            
            print("✓ .env file created from template")
            print("📝 Please edit .env file with your database credentials")
            return True
        except Exception as e:
            print(f"✗ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  .env.example not found. Please create .env manually")
        return False

def check_mysql():
    """Check if MySQL is available"""
    print("\n🗄️  Checking MySQL availability...")
    
    # Try to connect to MySQL
    success, output = run_command(["mysql", "--version"])
    if success:
        print("✓ MySQL is available")
        print("📝 Don't forget to create the database:")
        print("   CREATE DATABASE task_management;")
        return True
    else:
        print("⚠️  MySQL not found in PATH. Please ensure MySQL is installed and accessible")
        return False

def print_next_steps():
    """Print the next steps for the user"""
    activation_cmd = get_activation_command()
    
    print(f"""
🎉 Setup Complete!

Next steps:
1. Activate the virtual environment:
   {activation_cmd}

2. Create MySQL database:
   mysql -u root -p
   CREATE DATABASE task_management;
   exit

3. Edit .env file with your database credentials:
   DATABASE_URL=mysql+pymysql://username:password@localhost:3306/task_management

4. Run the application:
   uvicorn main:app --reload

5. Access the API:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

6. Test the API:
   python test_examples.py

When done, deactivate the virtual environment:
   deactivate
""")

def main():
    """Main setup function"""
    print("🚀 Task Management API - Local Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Check MySQL
    check_mysql()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()