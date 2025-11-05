# Krisp Python SDK Installation

1. **Download SDK**
   Download the latest **Python SDK v1.4.0** from the SDK Portal.
   For VIVA, check the `krisp_audio_test.py` sample for reference.

   > 💡 *Recommended:* Save the SDK inside `src/piopiy/audio/krisp` so all Krisp-related files stay together.

2. **Unzip & Locate Wheel**
   Unzip the SDK. Inside the `dist/` folder, choose the `.whl` file matching your setup.
   Example (Python 3.11, Linux x86_64):

   ```
   src/piopiy/audio/krisp/krisp-audio-sdk-python-1.4.0/dist/krisp_audio-1.4.0-cp311-cp311-linux_x86_64.whl
   ```

3. **Install SDK**

   ```bash
   cd src/piopiy/audio/krisp/krisp-audio-sdk-python-1.4.0/dist
   pip install krisp_audio-1.4.0-cp311-cp311-linux_x86_64.whl
   ```

   Verify installation:

   ```bash
   pip show krisp_audio
   ```

4. **Download Model**
   Download the **VIVA model package** (`krisp-viva-models-9.9`) from the same SDK Portal.
   Inside it, you’ll find several `.kef` model files — choose the **`krisp-viva-tel-v2.kef`** model, as it performs best for real-time and WebRTC/WebSocket-based audio.

5. **Set Environment Variable**
   In your `.env` file, add:

   ```bash
   KRISP_MODEL_PATH=/home/user/voice/agents/src/piopiy/audio/krisp/krisp-viva-models-9.9/krisp-viva-tel-v2.kef
   ```
