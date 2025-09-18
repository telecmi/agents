import os
import urllib.request
from pathlib import Path
import sys

def download_kokoro_models():
    """Download Kokoro model files during installation."""
    print("🎯 Downloading Kokoro model files...")
    
    # Get the target directory - this works both during development and after installation
    try:
        # Try to get the package directory
        import piopiy
        package_dir = Path(piopiy.__file__).parent
    except ImportError:
        # Fallback to current directory structure during development
        package_dir = Path(__file__).parent
    
    target_dir = package_dir / "services/opensource/kokoro/data"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if files already exist
    onnx_path = target_dir / "kokoro-v1.0.onnx"
    bin_path = target_dir / "voices-v1.0.bin"
    
    if onnx_path.exists() and bin_path.exists():
        print("✅ Kokoro files already exist, skipping download")
        return
    
    # URLs
    model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
    voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
    
    def download_with_progress(url, filepath):
        """Download file with progress indication."""
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(100, (downloaded * 100) // total_size)
                size_mb = total_size / (1024 * 1024)
                downloaded_mb = downloaded / (1024 * 1024)
                sys.stdout.write(f"\r  Progress: {percent}% ({downloaded_mb:.1f}/{size_mb:.1f} MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, filepath, progress_hook)
        print()  # New line after progress
    
    try:
        print("📥 Downloading kokoro-v1.0.onnx...")
        download_with_progress(model_url, onnx_path)
        print("✅ Downloaded kokoro-v1.0.onnx")
        
        print("📥 Downloading voices-v1.0.bin...")
        download_with_progress(voices_url, bin_path)
        print("✅ Downloaded voices-v1.0.bin")
        
        print("🎉 Kokoro model files downloaded successfully!")
        print(f"📁 Files saved to: {target_dir}")
        
        # List the downloaded files
        if onnx_path.exists() and bin_path.exists():
            print("Files:")
            print(f"  - {onnx_path.name}: {onnx_path.stat().st_size / (1024*1024):.1f} MB")
            print(f"  - {bin_path.name}: {bin_path.stat().st_size / (1024*1024):.1f} MB")
            
    except Exception as e:
        print(f"❌ Failed to download files: {e}")
        print("You can run the download manually later using the download_kokoro.sh script")
        # Don't raise the exception to avoid breaking the installation
        return

# if __name__ == "__main__":
#     download_kokoro_models()


def download_silero_model():
    """Download Silero TTS model file during installation."""
    print("🎯 Downloading Silero TTS model...")
    
    # Get the target directory - works both in development and after installation
    try:
        import piopiy
        package_dir = Path(piopiy.__file__).parent
    except ImportError:
        package_dir = Path(__file__).parent
    
    target_dir = package_dir / "audio/vad/data"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Model path
    model_path = target_dir / "silero_vad.onnx"
    
    if model_path.exists():
        print("✅ Silero model already exists, skipping download")
        return
    
    # Model URL (English TTS model)
    model_url = "https://huggingface.co/onnx-community/silero-vad/resolve/main/onnx/model.onnx"
    
    
    def download_with_progress(url, filepath):
        """Download file with progress indication."""
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(100, (downloaded * 100) // total_size)
                size_mb = total_size / (1024 * 1024)
                downloaded_mb = downloaded / (1024 * 1024)
                sys.stdout.write(f"\r  Progress: {percent}% ({downloaded_mb:.1f}/{size_mb:.1f} MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, filepath, progress_hook)
        print()  # newline after progress
    
    try:
        print("📥 Downloading silero_tts.pt...")
        download_with_progress(model_url, model_path)
        print("✅ Downloaded silero_tts.pt")
        
        print("🎉 Silero model file downloaded successfully!")
        print(f"📁 File saved to: {target_dir}")
        print(f"  - {model_path.name}: {model_path.stat().st_size / (1024*1024):.1f} MB")
            
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        print("You can run the download manually later")
        return
    

if __name__ == "__main__":
    download_kokoro_models()
    download_silero_model()
