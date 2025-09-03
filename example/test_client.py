import asyncio
import json
import websockets
import base64
import wave
import io
from typing import Optional, List, Dict, Any
from loguru import logger
import time


class ChatterboxTTSClient:
    """Direct WebSocket client for Chatterbox TTS service"""
    
    def __init__(
        self,
        websocket_url: str = "ws://103.247.19.245:60027",
        chunk_size: int = 75,
        exaggeration: float = 0.5,
        temperature: float = 0.8,
        cfg_weight: float = 0.5,
        context_window: int = 70,
        fade_duration: float = 0.09,
        sample_rate: int = 24000
    ):
        self.websocket_url = websocket_url
        self.chunk_size = chunk_size
        self.exaggeration = exaggeration
        self.temperature = temperature
        self.cfg_weight = cfg_weight
        self.context_window = context_window
        self.fade_duration = fade_duration
        self.sample_rate = sample_rate
        
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.current_session_id = None
        self.audio_chunks = []
        
    async def connect(self):
        """Connect to the Chatterbox WebSocket server"""
        try:
            logger.info(f"Connecting to Chatterbox server at {self.websocket_url}")
            self.websocket = await websockets.connect(
                self.websocket_url,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=5,
                max_size=16 * 1024 * 1024  # 16MB max message size
            )
            self.is_connected = True
            logger.info("Successfully connected to Chatterbox server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket server"""
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Disconnected from Chatterbox server")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
        self.is_connected = False
        self.websocket = None
    
    async def synthesize_non_streaming(self, text: str, output_file: Optional[str] = None) -> List[bytes]:
        """
        Synthesize speech using non-streaming mode
        
        Args:
            text: Text to synthesize
            output_file: Optional WAV file path to save audio
            
        Returns:
            List of audio chunks as bytes
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to server. Call connect() first.")
        
        request_id = f"req_{int(time.time())}"
        
        # Prepare synthesis request
        request = {
            "type": "synthesize",
            "text": text,
            "request_id": request_id,
            "params": {
                "chunk_size": self.chunk_size,
                "exaggeration": self.exaggeration,
                "temperature": self.temperature,
                "cfg_weight": self.cfg_weight,
                "context_window": self.context_window,
                "fade_duration": self.fade_duration
            }
        }
        
        logger.info(f"Synthesizing text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # Send request
        await self.websocket.send(json.dumps(request))
        
        audio_chunks = []
        
        # Receive response
        while True:
            try:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                
                # Parse JSON response
                data = json.loads(message)
                
                if data["type"] == "audio":
                    # Decode base64 audio
                    audio_bytes = base64.b64decode(data["audio_content"])
                    audio_chunks.append(audio_bytes)
                    logger.debug(f"Received audio chunk: {len(audio_bytes)} bytes")
                    
                elif data["type"] == "synthesis_complete":
                    logger.info(f"Synthesis completed for request {request_id}")
                    break
                    
                elif data["type"] == "error":
                    error_msg = data.get('error', 'Unknown error')
                    logger.error(f"Synthesis error: {error_msg}")
                    raise RuntimeError(f"Synthesis error: {error_msg}")
                    
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for synthesis response")
                raise RuntimeError("Synthesis timeout")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {e}")
                continue
        
        # Save to file if requested
        if output_file and audio_chunks:
            await self._save_audio_to_wav(audio_chunks, output_file)
        
        return audio_chunks
    
    async def synthesize_streaming(
        self, 
        text: str, 
        output_file: Optional[str] = None,
        on_chunk_callback: Optional[callable] = None
    ) -> List[bytes]:
        """
        Synthesize speech using streaming mode
        
        Args:
            text: Text to synthesize
            output_file: Optional WAV file path to save audio
            on_chunk_callback: Optional callback function called for each audio chunk
            
        Returns:
            List of audio chunks as bytes
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to server. Call connect() first.")
        
        session_id = f"session_{int(time.time())}"
        self.current_session_id = session_id
        
        logger.info(f"Starting streaming synthesis for session {session_id}")
        
        # Send stream_start
        stream_start = {
            "type": "stream_start",
            "session_id": session_id,
            "params": {
                "chunk_size": self.chunk_size,
                "exaggeration": self.exaggeration,
                "temperature": self.temperature,
                "cfg_weight": self.cfg_weight,
                "context_window": self.context_window,
                "fade_duration": self.fade_duration
            }
        }
        
        await self.websocket.send(json.dumps(stream_start))
        logger.info("Sent stream_start message")
        
        # Wait for stream_ready
        logger.info("Waiting for stream_ready response...")
        while True:
            try:
                msg = await asyncio.wait_for(self.websocket.recv(), timeout=20.0)
            except asyncio.TimeoutError:
                raise RuntimeError("Timeout waiting for stream_ready")
            
            if isinstance(msg, str):
                try:
                    data = json.loads(msg)
                except json.JSONDecodeError:
                    continue
                    
                if (data.get("type") == "stream_ready" and 
                    data.get("session_id") == session_id):
                    logger.info(f"Stream ready for session {session_id}")
                    break
                elif data.get("type") == "error":
                    error_msg = data.get('error', 'Unknown error')
                    raise RuntimeError(f"Server error: {error_msg}")
        
        # Send text and flush
        await asyncio.gather(
            self.websocket.send(json.dumps({
                "type": "stream_text",
                "text": text
            })),
            self.websocket.send(json.dumps({
                "type": "stream_flush"
            }))
        )
        
        logger.info("Sent text and flush messages")
        
        audio_chunks = []
        chunk_count = 0
        stream_completed = False
        
        # Receive audio stream
        try:
            while True:
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    
                    if isinstance(message, str):
                        data = json.loads(message)
                        
                        if data["type"] == "audio_chunk":
                            # Next message should be binary audio data
                            audio_data = await asyncio.wait_for(
                                self.websocket.recv(), timeout=0.1
                            )
                            
                            if isinstance(audio_data, bytes):
                                audio_chunks.append(audio_data)
                                chunk_count += 1
                                
                                # Call callback if provided
                                if on_chunk_callback:
                                    await on_chunk_callback(audio_data, chunk_count)
                                    
                                logger.debug(f"Received audio chunk {chunk_count}: {len(audio_data)} bytes")
                        
                        elif data["type"] == "stream_complete":
                            logger.info(f"Stream completed for session {session_id}, {chunk_count} chunks")
                            stream_completed = True
                            break
                            
                        elif data["type"] == "error":
                            error_msg = data.get('error', 'Unknown error')
                            logger.error(f"Stream error: {error_msg}")
                            raise RuntimeError(f"Stream error: {error_msg}")
                    
                    elif isinstance(message, bytes):
                        # Direct binary audio data
                        audio_chunks.append(message)
                        chunk_count += 1
                        
                        if on_chunk_callback:
                            await on_chunk_callback(message, chunk_count)
                            
                        logger.debug(f"Received binary audio chunk {chunk_count}: {len(message)} bytes")
                        
                except asyncio.TimeoutError:
                    # Check if we should continue waiting
                    if stream_completed:
                        break
                    continue
                    
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            raise
        finally:
            # Send stream_end if not completed
            if not stream_completed:
                try:
                    await self.websocket.send(json.dumps({"type": "stream_end"}))
                    logger.info("Sent stream_end")
                except Exception as e:
                    logger.error(f"Error sending stream_end: {e}")
            
            self.current_session_id = None
        
        # Save to file if requested
        if output_file and audio_chunks:
            await self._save_audio_to_wav(audio_chunks, output_file)
        
        return audio_chunks
    
    async def _save_audio_to_wav(self, audio_chunks: List[bytes], output_file: str):
        """Save audio chunks to a WAV file"""
        try:
            # Combine all audio chunks
            combined_audio = b''.join(audio_chunks)
            
            # Create WAV file
            with wave.open(output_file, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(combined_audio)
            
            logger.info(f"Audio saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving audio to {output_file}: {e}")
    
    async def stop_current_synthesis(self):
        """Stop the current synthesis session"""
        if self.current_session_id and self.is_connected:
            try:
                await self.websocket.send(json.dumps({"type": "stream_end"}))
                logger.info(f"Stopped synthesis for session {self.current_session_id}")
                self.current_session_id = None
            except Exception as e:
                logger.error(f"Error stopping synthesis: {e}")


# Example usage and test functions
class ChatterboxClientExample:
    """Example usage of the Chatterbox TTS Client"""
    
    def __init__(self):
        self.client = ChatterboxTTSClient()
    
    async def test_non_streaming(self):
        """Test non-streaming synthesis"""
        text = "Hello, this is a test of the Chatterbox text-to-speech system using non-streaming mode."
        
        try:
            await self.client.connect()
            audio_chunks = await self.client.synthesize_non_streaming(
                text, 
                output_file="output_non_streaming.wav"
            )
            logger.info(f"Generated {len(audio_chunks)} audio chunks")
            
        except Exception as e:
            logger.error(f"Non-streaming test failed: {e}")
        finally:
            await self.client.disconnect()
    
    async def test_streaming(self):
        """Test streaming synthesis"""
        text = "This is a test of the Chatterbox streaming synthesis mode. It should provide real-time audio generation."
        
        async def chunk_callback(audio_data: bytes, chunk_num: int):
            logger.info(f"Received streaming chunk {chunk_num}: {len(audio_data)} bytes")
        
        try:
            await self.client.connect()
            audio_chunks = await self.client.synthesize_streaming(
                text,
                output_file="output_streaming.wav",
                on_chunk_callback=chunk_callback
            )
            logger.info(f"Generated {len(audio_chunks)} audio chunks via streaming")
            
        except Exception as e:
            logger.error(f"Streaming test failed: {e}")
        finally:
            await self.client.disconnect()
    
    async def test_custom_parameters(self):
        """Test synthesis with custom parameters"""
        # Create client with custom parameters
        custom_client = ChatterboxTTSClient(
            chunk_size=100,
            exaggeration=0.7,
            temperature=0.9,
            cfg_weight=0.6
        )
        
        text = "Testing custom parameters for more expressive speech synthesis."
        
        try:
            await custom_client.connect()
            audio_chunks = await custom_client.synthesize_streaming(
                text,
                output_file="output_custom.wav"
            )
            logger.info(f"Custom parameters test: {len(audio_chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Custom parameters test failed: {e}")
        finally:
            await custom_client.disconnect()


# Main execution
async def main():
    """Main function to run examples"""
    example = ChatterboxClientExample()
    
    logger.info("Testing Chatterbox TTS Client")
    
    # Test non-streaming mode
    logger.info("=== Testing Non-Streaming Mode ===")
    await example.test_non_streaming()
    
    await asyncio.sleep(1)
    
    # Test streaming mode
    logger.info("=== Testing Streaming Mode ===")
    await example.test_streaming()
    
    await asyncio.sleep(1)
    
    # Test custom parameters
    logger.info("=== Testing Custom Parameters ===")
    await example.test_custom_parameters()


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    # Run the examples
    asyncio.run(main())