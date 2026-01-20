#!/usr/bin/env python3
"""
Start script for Social Media Automation API
"""

import subprocess
import sys
import os
import time
import importlib

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []

    # Check backend dependencies
    backend_deps = ['fastapi', 'uvicorn', 'sqlalchemy', 'passlib', 'jose']
    for dep in backend_deps:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)

    # Check if npm is available
    npm_available = False
    try:
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
        npm_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return missing_deps, npm_available

def install_missing_deps(missing_deps):
    """Try to install missing dependencies"""
    if missing_deps:
        print(f"Installing missing dependencies: {', '.join(missing_deps)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_deps)
            print("Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install dependencies. Please run:")
            print(f"   pip install {' '.join(missing_deps)}")
            return False
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("Starting Social Media Automation API...")
    print("Backend will be available at: http://localhost:8000")
    print("API Documentation at: http://localhost:8000/docs")

    # Change to the correct directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)

    # Start the backend
    try:
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        return backend_process
    except FileNotFoundError:
        print("❌ uvicorn not found. Please install it with:")
        print("   pip install uvicorn")
        return None

def start_frontend():
    """Start the React frontend"""
    print("\nStarting React Frontend...")
    print("Frontend will be available at: http://localhost:3000")

    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

    if not os.path.exists(frontend_dir):
        print("Frontend directory not found.")
        print("To set up the frontend, run:")
        print("   cd frontend")
        print("   npm install")
        return None

    # Check if package.json exists
    if not os.path.exists(os.path.join(frontend_dir, "package.json")):
        print("Frontend package.json not found.")
        return None

    # Check if node_modules exists
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("Frontend dependencies not installed.")
        print("To install frontend dependencies, run:")
        print("   cd frontend")
        print("   npm install")
        return None

    try:
        # Start the frontend (this will block until Ctrl+C)
        frontend_process = subprocess.Popen([
            "npm", "start"
        ], cwd=frontend_dir)

        return frontend_process
    except FileNotFoundError:
        print("npm not found. Please install Node.js and npm:")
        print("   https://nodejs.org/")
        return None

def main():
    print("Social Media Automation Platform")
    print("=" * 50)

    # Check dependencies
    missing_deps, npm_available = check_dependencies()

    if missing_deps:
        print(f"Missing backend dependencies: {', '.join(missing_deps)}")
        if install_missing_deps(missing_deps):
            print("Dependencies installed successfully. Please run the script again.")
        else:
            print("Please install the missing dependencies manually.")
        return

    if not npm_available:
        print("npm not found. Frontend will not start.")
        print("To install Node.js and npm: https://nodejs.org/")

    try:
        # Start backend
        backend_process = start_backend()

        if backend_process is None:
            print("Failed to start backend")
            return

        # Wait a moment for backend to start
        time.sleep(3)

        # Try to start frontend
        frontend_process = start_frontend()

        if frontend_process:
            print("\nBoth services started successfully!")
            print("\nOpen your browser and visit:")
            print("   Dashboard: http://localhost:3000")
            print("   API Docs: http://localhost:8000/docs")
            print("   Basic UI: http://localhost:8000")
            print("\nPress Ctrl+C to stop both services")

            # Wait for processes to complete
            try:
                backend_process.wait()
            except KeyboardInterrupt:
                pass
        else:
            print("\nBackend started successfully!")
            print("Frontend not available (npm/Node.js not installed)")
            print("\nYou can still access:")
            print("   API Docs: http://localhost:8000/docs")
            print("   API Base: http://localhost:8000/api")
            print("   Basic Web UI: http://localhost:8000")
            print("   Static HTML: Open index.html in your browser")
            print("\nPress Ctrl+C to stop the backend")

            # Wait for backend process
            try:
                backend_process.wait()
            except KeyboardInterrupt:
                pass

    except KeyboardInterrupt:
        print("\n\nShutting down services...")
        if 'backend_process' in locals() and backend_process:
            backend_process.terminate()
        if 'frontend_process' in locals() and frontend_process:
            frontend_process.terminate()
        print("Services stopped")

if __name__ == "__main__":
    main()