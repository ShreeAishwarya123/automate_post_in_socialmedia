"""
Smart dependency installer
Installs packages one by one to identify any problematic packages
"""

import subprocess
import sys

# Core packages that should install without issues
CORE_PACKAGES = [
    "requests>=2.31.0",
    "pyyaml>=6.0.0",
    "schedule>=1.2.0",
    "python-dotenv>=1.0.0",
    "Pillow>=10.0.0",
]

# Social media platform packages
PLATFORM_PACKAGES = [
    "instagrapi>=2.0.0",
    "facebook-sdk>=3.1.0",
    "google-api-python-client>=2.100.0",
    "google-auth-httplib2>=0.1.1",
    "google-auth-oauthlib>=1.1.0",
]

def install_package(package):
    """Install a single package"""
    print(f"\n{'='*60}")
    print(f"Installing: {package}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("="*60)
    print("Social Media Automation - Dependency Installer")
    print("="*60)
    
    # First, upgrade pip, setuptools, wheel
    print("\n📦 Upgrading pip, setuptools, and wheel...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
            check=True
        )
        print("✓ pip, setuptools, and wheel upgraded")
    except subprocess.CalledProcessError:
        print("⚠ Warning: Could not upgrade pip/setuptools/wheel")
        print("Continuing anyway...")
    
    # Install core packages
    print("\n📦 Installing core packages...")
    core_failed = []
    for package in CORE_PACKAGES:
        if not install_package(package):
            core_failed.append(package)
    
    # Install platform packages
    print("\n📦 Installing platform packages...")
    platform_failed = []
    for package in PLATFORM_PACKAGES:
        if not install_package(package):
            platform_failed.append(package)
    
    # Summary
    print("\n" + "="*60)
    print("Installation Summary")
    print("="*60)
    
    if not core_failed and not platform_failed:
        print("✓ All packages installed successfully!")
        return 0
    else:
        print("\n⚠ Some packages failed to install:")
        if core_failed:
            print("\nCore packages that failed:")
            for pkg in core_failed:
                print(f"  - {pkg}")
        if platform_failed:
            print("\nPlatform packages that failed:")
            for pkg in platform_failed:
                print(f"  - {pkg}")
        
        print("\n💡 Suggestions:")
        print("1. Try installing failed packages individually")
        print("2. Check INSTALL_TROUBLESHOOTING.md for solutions")
        print("3. Some platforms may work even if their package failed")
        print("4. Consider using Python 3.11 for better compatibility")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())


