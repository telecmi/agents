import subprocess
import sys
import os
from pathlib import Path
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

def run_kokoro_download():
    """Run the kokoro download bash script"""
    
    script_path = Path(__file__).parent / "download_kokoro.sh"
    
    if not script_path.exists():
        print(f"⚠️  Warning: Download script not found at {script_path}")
        return
    
    print("🎯 Running Kokoro download script...")
    try:
        # Make script executable
        subprocess.run(["chmod", "+x", str(script_path)], check=True)
        
        # Run the script and show output in real-time
        process = subprocess.Popen(
            ["/bin/bash", str(script_path)],
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ Kokoro download script completed successfully!")
        else:
            print(f"⚠️  Warning: Download script failed with return code {process.returncode}")
            
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Failed to run download script: {e}")
    except Exception as e:
        print(f"⚠️  Warning: Unexpected error: {e}")

class PostDevelopCommand(develop):
    """Post-installation for development mode (pip install -e .)"""
    def run(self):
        print("🔧 Running develop command...")
        develop.run(self)
        print("🔧 Development installation complete, running kokoro download...")
        run_kokoro_download()

class PostInstallCommand(install):
    """Post-installation for installation mode"""
    def run(self):
        print("🔧 Running install command...")
        install.run(self)
        print("🔧 Installation complete, running kokoro download...")
        run_kokoro_download()

# Use setup() to add custom commands while keeping pyproject.toml configuration
setup(
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)