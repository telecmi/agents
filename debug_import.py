import sys
import os

try:
    import piopiy.transports.services.telecmi as telecmi
    print(f"✅ Import successful!")
    print(f"📍 File location: {telecmi.__file__}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("🔎 sys.path:")
    for p in sys.path:
        print(f"  - {p}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
