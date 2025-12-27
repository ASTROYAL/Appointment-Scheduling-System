#!/usr/bin/env python3
"""
Simple startup script for the Appointment Scheduling System
"""

import subprocess
import sys
import time
import threading
from pathlib import Path

def start_backend():
    """Start the Flask backend server"""
    print("🐍 Starting Flask backend server on http://localhost:5000...")
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")

def start_frontend():
    """Start the React frontend development server"""
    print("⚛️ Starting React frontend server on http://localhost:3000...")
    try:
        subprocess.run(['npm', 'run', 'dev'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")

def main():
    print("🚀 Appointment Scheduling System")
    print("=" * 50)
    
    # Check if required files exist
    if not Path('appointment_service.py').exists():
        print("❌ appointment_service.py not found")
        return 1
    
    if not Path('package.json').exists():
        print("❌ package.json not found")
        return 1
    
    # Install npm dependencies if needed
    if not Path('node_modules').exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(['npm', 'install'], check=True)
            print("✅ Dependencies installed!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Make sure Node.js is installed.")
            return 1
    
    print("\n🌐 Starting servers...")
    print("   Backend:  http://localhost:5000")
    print("   Frontend: http://localhost:3000")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    # Start backend in separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(2)
    
    try:
        # Start frontend (blocks until Ctrl+C)
        start_frontend()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        return 0

if __name__ == '__main__':
    sys.exit(main())