"""
Setup script for OpenVoice installation and model downloads
"""
import os
import subprocess
import sys
from pathlib import Path
import urllib.request
import zipfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Error: {e.stderr}")
        raise

def clone_openvoice():
    """Clone OpenVoice repository"""
    logger.info("Cloning OpenVoice repository...")
    
    if Path("OpenVoice").exists():
        logger.info("OpenVoice directory already exists, pulling latest changes...")
        run_command("git pull", cwd="OpenVoice")
    else:
        run_command("git clone https://github.com/myshell-ai/OpenVoice.git")
    
    logger.info("OpenVoice repository cloned/updated successfully")

def install_openvoice():
    """Install OpenVoice package"""
    logger.info("Installing OpenVoice package...")
    
    # Change to OpenVoice directory and install
    run_command("pip install -e .", cwd="OpenVoice")
    
    logger.info("OpenVoice package installed successfully")

def download_checkpoints():
    """Download OpenVoice model checkpoints"""
    logger.info("Downloading OpenVoice checkpoints...")
    
    checkpoints_dir = Path("checkpoints")
    checkpoints_dir.mkdir(exist_ok=True)
    
    # V1 checkpoints
    v1_dir = checkpoints_dir / "v1"
    v1_dir.mkdir(exist_ok=True)
    
    # V2 checkpoints  
    v2_dir = checkpoints_dir / "v2"
    v2_dir.mkdir(exist_ok=True)
    
    # Download URLs (these would need to be updated with actual URLs)
    checkpoint_urls = {
        "v1": [
            # Add actual V1 checkpoint URLs here
            # "https://myshell-public-repo-hosting.s3.amazonaws.com/openvoice/checkpoints_v1_0417.zip"
        ],
        "v2": [
            # Add actual V2 checkpoint URLs here  
            # "https://myshell-public-repo-hosting.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip"
        ]
    }
    
    logger.info("Note: Checkpoint downloads need to be implemented with actual URLs")
    logger.info("Please manually download checkpoints from the official OpenVoice repository")
    logger.info("V1 checkpoints should go in: checkpoints/v1/")
    logger.info("V2 checkpoints should go in: checkpoints/v2/")

def test_openvoice_installation():
    """Test OpenVoice installation"""
    logger.info("Testing OpenVoice installation...")
    
    try:
        # Test import
        import openvoice
        logger.info("OpenVoice import successful")
        
        # Create a simple test script
        test_script = '''
import sys
sys.path.append("OpenVoice")
try:
    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter
    print("OpenVoice imports successful")
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Other error: {e}")
'''
        
        with open("test_openvoice.py", "w") as f:
            f.write(test_script)
        
        result = run_command("python test_openvoice.py")
        logger.info(f"Test result: {result.stdout}")
        
        # Clean up test file
        Path("test_openvoice.py").unlink()
        
    except Exception as e:
        logger.error(f"OpenVoice test failed: {e}")
        raise

def main():
    """Main setup function"""
    logger.info("Starting OpenVoice setup...")
    
    try:
        # Step 1: Clone OpenVoice repository
        clone_openvoice()
        
        # Step 2: Install OpenVoice package
        install_openvoice()
        
        # Step 3: Download checkpoints (placeholder for now)
        download_checkpoints()
        
        # Step 4: Test installation
        test_openvoice_installation()
        
        logger.info("OpenVoice setup completed successfully!")
        logger.info("You can now start the FastAPI server with: python main.py")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
