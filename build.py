#!/usr/bin/env python3
"""
Build script for deployment preparation
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🔨 Building Appointment Scheduling System for Deployment")
    print("=" * 60)
    
    # Check if Node.js is available
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        print("✅ Node.js found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found. Please install Node.js for deployment.")
        return 1
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.run(['npm', 'install'], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return 1
    
    # Build frontend
    print("🏗️ Building frontend...")
    try:
        subprocess.run(['npm', 'run', 'build'], check=True)
        print("✅ Frontend built successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to build frontend")
        return 1
    
    # Check Python dependencies
    print("🐍 Checking Python dependencies...")
    try:
        import flask
        import flask_cors
        from appointment_service import get_appointments
        print("✅ Python dependencies available")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return 1
    
    print("\n🎉 Build completed successfully!")
    print("📁 Files ready for deployment:")
    print("   - app.py (Flask backend)")
    print("   - appointment_service.py (Core logic)")
    print("   - EMR_Frontend_Assignment.jsx (Main frontend)")
    print("   - dist/ (Built frontend assets)")
    print("   - requirements.txt (Python deps)")
    print("   - vercel.json (Deployment config)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())