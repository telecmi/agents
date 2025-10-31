# #
# # Copyright (c) 2024–2025, Daily
# #
# # SPDX-License-Identifier: BSD 2-Clause License
# #

# """Smart Turn V3 detection implementation for Pipecat.

# This module provides a turn detection analyzer based on the Smart Turn V3 ONNX model,
# which can detect natural turn-taking endpoints in conversational audio with high accuracy.
# Supports 16kHz sample rate and 23 languages.
# """

# from typing import Optional

# import numpy as np
# from loguru import logger

# from piopiy.audio.vad.vad_analyzer import VADAnalyzer, VADParams

# try:
#     import onnxruntime
#     from transformers import WhisperFeatureExtractor
# except ModuleNotFoundError as e:
#     logger.error(f"Exception: {e}")
#     logger.error(
#         "In order to use Smart Turn V3, you need to `pip install transformers onnxruntime`."
#     )
#     raise Exception(f"Missing module(s): {e}")


# class SmartTurnV3Model:
#     """ONNX runtime wrapper for the Smart Turn V3 model.

#     Provides turn detection using the pre-trained Smart Turn V3 model
#     with ONNX runtime for efficient CPU inference. Handles audio preprocessing
#     and prediction of conversation turn endpoints.
#     """

#     def __init__(self, model_path: str, force_onnx_cpu: bool = True):
#         """Initialize the Smart Turn V3 ONNX model.

#         Args:
#             model_path: Path to the ONNX model file.
#             force_onnx_cpu: Whether to force CPU execution provider.
#         """
#         # Configure ONNX session for optimal CPU performance
#         opts = onnxruntime.SessionOptions()
#         opts.execution_mode = onnxruntime.ExecutionMode.ORT_SEQUENTIAL
#         opts.inter_op_num_threads = 1
#         opts.intra_op_num_threads = 1
#         opts.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL

#         if force_onnx_cpu and "CPUExecutionProvider" in onnxruntime.get_available_providers():
#             self.session = onnxruntime.InferenceSession(
#                 model_path, providers=["CPUExecutionProvider"], sess_options=opts
#             )
#         else:
#             self.session = onnxruntime.InferenceSession(model_path, sess_options=opts)

#         # Initialize Whisper feature extractor for audio preprocessing
#         self.feature_extractor = WhisperFeatureExtractor(chunk_length=8)
        
#         self.sample_rate = 16000
#         self.max_duration_seconds = 8

#         logger.debug("Smart Turn V3 model initialized successfully")

#     def _truncate_or_pad_audio(self, audio_array: np.ndarray) -> np.ndarray:
#         """Truncate audio to last n seconds or pad with zeros to meet n seconds.
        
#         Args:
#             audio_array: Input audio array.
            
#         Returns:
#             Audio array truncated or padded to exactly 8 seconds.
#         """
#         max_samples = self.max_duration_seconds * self.sample_rate
        
#         if len(audio_array) > max_samples:
#             # Keep last 8 seconds
#             return audio_array[-max_samples:]
#         elif len(audio_array) < max_samples:
#             # Pad with zeros at the beginning
#             padding = max_samples - len(audio_array)
#             return np.pad(audio_array, (padding, 0), mode="constant", constant_values=0)
        
#         return audio_array

#     def _validate_input(self, audio_array: np.ndarray) -> np.ndarray:
#         """Validate and preprocess input audio data.
        
#         Args:
#             audio_array: Input audio array.
            
#         Returns:
#             Validated and normalized audio array.
            
#         Raises:
#             ValueError: If audio format is invalid.
#         """
#         # Ensure audio is 1D
#         if audio_array.ndim != 1:
#             raise ValueError(f"Audio must be 1D array, got shape {audio_array.shape}")
        
#         # Convert to float32 if needed
#         if audio_array.dtype != np.float32:
#             audio_array = audio_array.astype(np.float32)
        
#         # Normalize to [-1, 1] range if needed
#         max_val = np.max(np.abs(audio_array))
#         if max_val > 1.0:
#             audio_array = audio_array / max_val
            
#         return audio_array

#     def __call__(self, audio_array: np.ndarray, sr: int) -> float:
#         """Process audio input through the Smart Turn V3 model.

#         Args:
#             audio_array: Numpy array containing audio samples at 16kHz.
#             sr: Sample rate (must be 16000).

#         Returns:
#             Probability of turn completion (0.0 to 1.0).
#         """
#         if sr != self.sample_rate:
#             raise ValueError(f"Smart Turn V3 requires {self.sample_rate}Hz, got {sr}Hz")
        
#         # Validate input
#         audio_array = self._validate_input(audio_array)
        
#         # Truncate to 8 seconds (keeping the end) or pad to 8 seconds
#         audio_array = self._truncate_or_pad_audio(audio_array)

#         # Process audio using Whisper's feature extractor
#         inputs = self.feature_extractor(
#             audio_array,
#             sampling_rate=self.sample_rate,
#             return_tensors="np",
#             padding="max_length",
#             max_length=self.max_duration_seconds * self.sample_rate,
#             truncation=True,
#             do_normalize=True,
#         )

#         # Extract features and ensure correct shape for ONNX
#         input_features = inputs.input_features.squeeze(0).astype(np.float32)
#         input_features = np.expand_dims(input_features, axis=0)  # Add batch dimension

#         # Run ONNX inference
#         outputs = self.session.run(None, {"input_features": input_features})

#         # Extract probability (ONNX model returns sigmoid probabilities)
#         probability = float(outputs[0][0].item())

#         return probability


# class SmartTurnV3Analyzer(VADAnalyzer):
#     """Turn detection analyzer using the Smart Turn V3 model.

#     Implements turn endpoint detection using the pre-trained Smart Turn V3 ONNX model
#     for accurate conversation turn-taking detection. Supports 16kHz sample rate
#     and 23 languages including Arabic, Bengali, Chinese, Danish, Dutch, German,
#     English, Finnish, French, Hindi, Indonesian, Italian, Japanese, Korean, Marathi,
#     Norwegian, Polish, Portuguese, Russian, Spanish, Turkish, Ukrainian, and Vietnamese.
#     """

#     def __init__(
#         self,
#         *,
#         sample_rate: Optional[int] = None,
#         params: Optional[VADParams] = None,
#         model_path: Optional[str] = None,
#     ):
#         """Initialize the Smart Turn V3 analyzer.

#         Args:
#             sample_rate: Audio sample rate (must be 16000 Hz). If None, will be set to 16000.
#             params: VAD parameters for detection thresholds and timing.
#             model_path: Path to the ONNX model file. If None, will look for default location.
#         """
#         # Set default sample rate if not provided
#         if sample_rate is None:
#             sample_rate = 16000
        
#         # Validate sample rate before calling parent constructor
#         if sample_rate != 16000:
#             raise ValueError(
#                 f"Smart Turn V3 requires 16000 Hz sample rate (got: {sample_rate})"
#             )
        
#         # Call parent constructor with validated sample rate
#         super().__init__(sample_rate=sample_rate, params=params)

#         logger.debug("Loading Smart Turn V3 model...")

#         # Try to find model path if not provided
#         if model_path is None:
#             model_name = "smart-turn-v3.0.onnx"
#             package_path = "piopiy.audio.vad.data"

#             try:
#                 import importlib_resources as impresources

#                 model_path = str(impresources.files(package_path).joinpath(model_name))
#             except BaseException:
#                 from importlib import resources as impresources

#                 try:
#                     with impresources.path(package_path, model_name) as f:
#                         model_path = str(f)
#                 except BaseException:
#                     model_path = str(impresources.files(package_path).joinpath(model_name))

#         self._model = SmartTurnV3Model(model_path, force_onnx_cpu=False)
        
#         # Buffer for accumulating audio
#         self._audio_buffer = np.array([], dtype=np.float32)
#         self._min_audio_length = 0.5  # Minimum audio length in seconds for analysis
        
#         logger.debug("Loaded Smart Turn V3 model")

#     #
#     # VADAnalyzer
#     #

#     def set_sample_rate(self, sample_rate: int):
#         """Set the sample rate for audio processing.

#         Args:
#             sample_rate: Audio sample rate (must be 16000 Hz).

#         Raises:
#             ValueError: If sample rate is not 16000 Hz.
#         """
#         if sample_rate != 16000:
#             raise ValueError(f"Smart Turn V3 requires 16000Hz sample rate (got {sample_rate}Hz)")

#         super().set_sample_rate(sample_rate)

#     def num_frames_required(self) -> int:
#         """Get the number of audio frames required for analysis.

#         Returns:
#             Number of frames required (512 for 16kHz).
#         """
#         return 512

#     def voice_confidence(self, buffer) -> float:
#         """Calculate turn completion confidence for the given audio buffer.

#         Args:
#             buffer: Audio buffer to analyze (int16 PCM data).

#         Returns:
#             Turn completion confidence score between 0.0 and 1.0.
#         """
#         try:
#             # Get sample rate from parent class
#             sr = self.sample_rate
            
#             # If sample rate is not set yet, use default
#             if sr == 0:
#                 logger.warning("Sample rate not initialized, using 16000 Hz")
#                 sr = 16000
            
#             # Convert int16 buffer to float32 in range [-1.0, 1.0]
#             audio_int16 = np.frombuffer(buffer, np.int16)
#             audio_float32 = audio_int16.astype(np.float32) / 32768.0
            
#             # Accumulate audio in buffer
#             self._audio_buffer = np.concatenate([self._audio_buffer, audio_float32])
            
#             # Only analyze if we have enough audio
#             min_samples = int(self._min_audio_length * sr)
#             if len(self._audio_buffer) < min_samples:
#                 return 0.0
            
#             # Run model inference
#             turn_probability = self._model(self._audio_buffer, sr)
            
#             # Clear buffer after analysis
#             self._audio_buffer = np.array([], dtype=np.float32)
            
#             return turn_probability
            
#         except Exception as e:
#             logger.error(f"Error analyzing audio with Smart Turn V3: {e}")
#             import traceback
#             logger.error(traceback.format_exc())
#             # Reset buffer on error
#             self._audio_buffer = np.array([], dtype=np.float32)
#             return 0.0
    
























#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Smart Turn V3 detection implementation for Pipecat.

This module provides a turn detection analyzer based on the Smart Turn V3 ONNX model,
which can detect natural turn-taking endpoints in conversational audio with high accuracy.
Supports 16kHz sample rate and 23 languages.
"""

from typing import Optional

import numpy as np
from loguru import logger

from piopiy.audio.vad.vad_analyzer import VADAnalyzer, VADParams

try:
    import onnxruntime
    from transformers import WhisperFeatureExtractor
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error(
        "In order to use Smart Turn V3, you need to `pip install transformers onnxruntime-gpu`."
    )
    raise Exception(f"Missing module(s): {e}")


class SmartTurnV3Model:
    """ONNX runtime wrapper for the Smart Turn V3 model.

    Provides turn detection using the pre-trained Smart Turn V3 model
    with ONNX runtime for efficient GPU inference. Handles audio preprocessing
    and prediction of conversation turn endpoints.
    """

    def __init__(self, model_path: str, force_onnx_cpu: bool = False):
        """Initialize the Smart Turn V3 ONNX model.

        Args:
            model_path: Path to the ONNX model file.
            force_onnx_cpu: Whether to force CPU execution provider (deprecated, now uses GPU).
        """
        # Configure ONNX session for GPU performance
        opts = onnxruntime.SessionOptions()
        opts.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL

        # Use GPU execution providers (CUDA or TensorRT)
        providers = []
        available_providers = onnxruntime.get_available_providers()
        
        if "CUDAExecutionProvider" in available_providers:
            providers.append("CUDAExecutionProvider")
        if "TensorrtExecutionProvider" in available_providers:
            providers.append("TensorrtExecutionProvider")
        
        if not providers:
            logger.warning("No GPU providers available, falling back to CPU")
            providers = ["CPUExecutionProvider"]
        
        self.session = onnxruntime.InferenceSession(
            model_path, providers=providers, sess_options=opts
        )

        # Initialize Whisper feature extractor for audio preprocessing
        self.feature_extractor = WhisperFeatureExtractor(chunk_length=10)
        
        self.sample_rate = 16000
        self.max_duration_seconds = 8

        logger.debug("Smart Turn V3 model initialized successfully")

    def _truncate_or_pad_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """Truncate audio to last n seconds or pad with zeros to meet n seconds.
        
        Args:
            audio_array: Input audio array.
            
        Returns:
            Audio array truncated or padded to exactly 8 seconds.
        """
        max_samples = self.max_duration_seconds * self.sample_rate
        
        if len(audio_array) > max_samples:
            # Keep last 8 seconds
            return audio_array[-max_samples:]
        elif len(audio_array) < max_samples:
            # Pad with zeros at the beginning
            padding = max_samples - len(audio_array)
            return np.pad(audio_array, (padding, 0), mode="constant", constant_values=0)
        
        return audio_array

    def _validate_input(self, audio_array: np.ndarray) -> np.ndarray:
        """Validate and preprocess input audio data.
        
        Args:
            audio_array: Input audio array.
            
        Returns:
            Validated and normalized audio array.
            
        Raises:
            ValueError: If audio format is invalid.
        """
        # Ensure audio is 1D
        if audio_array.ndim != 1:
            raise ValueError(f"Audio must be 1D array, got shape {audio_array.shape}")
        
        # Convert to float32 if needed
        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)
        
        # Normalize to [-1, 1] range if needed
        max_val = np.max(np.abs(audio_array))
        if max_val > 1.0:
            audio_array = audio_array / max_val
            
        return audio_array

    def __call__(self, audio_array: np.ndarray, sr: int) -> float:
        """Process audio input through the Smart Turn V3 model.

        Args:
            audio_array: Numpy array containing audio samples at 16kHz.
            sr: Sample rate (must be 16000).

        Returns:
            Probability of turn completion (0.0 to 1.0).
        """
        if sr != self.sample_rate:
            raise ValueError(f"Smart Turn V3 requires {self.sample_rate}Hz, got {sr}Hz")
        
        # Validate input
        audio_array = self._validate_input(audio_array)
        
        # Truncate to 8 seconds (keeping the end) or pad to 8 seconds
        audio_array = self._truncate_or_pad_audio(audio_array)

        # Process audio using Whisper's feature extractor
        inputs = self.feature_extractor(
            audio_array,
            sampling_rate=self.sample_rate,
            return_tensors="np",
            padding="max_length",
            max_length=self.max_duration_seconds * self.sample_rate,
            truncation=True,
            do_normalize=True,
        )

        # Extract features and ensure correct shape for ONNX
        input_features = inputs.input_features.squeeze(0).astype(np.float32)
        input_features = np.expand_dims(input_features, axis=0)  # Add batch dimension

        # Run ONNX inference
        outputs = self.session.run(None, {"input_features": input_features})

        # Extract probability (ONNX model returns sigmoid probabilities)
        probability = float(outputs[0][0].item())

        return probability


class SmartTurnV3Analyzer(VADAnalyzer):
    """Turn detection analyzer using the Smart Turn V3 model.

    Implements turn endpoint detection using the pre-trained Smart Turn V3 ONNX model
    for accurate conversation turn-taking detection. Supports 16kHz sample rate
    and 23 languages including Arabic, Bengali, Chinese, Danish, Dutch, German,
    English, Finnish, French, Hindi, Indonesian, Italian, Japanese, Korean, Marathi,
    Norwegian, Polish, Portuguese, Russian, Spanish, Turkish, Ukrainian, and Vietnamese.
    """

    def __init__(
        self,
        *,
        sample_rate: Optional[int] = None,
        params: Optional[VADParams] = None,
        model_path: Optional[str] = None,
    ):
        """Initialize the Smart Turn V3 analyzer.

        Args:
            sample_rate: Audio sample rate (must be 16000 Hz). If None, will be set to 16000.
            params: VAD parameters for detection thresholds and timing.
            model_path: Path to the ONNX model file. If None, will look for default location.
        """
        # Set default sample rate if not provided
        if sample_rate is None:
            sample_rate = 16000
        
        # Validate sample rate before calling parent constructor
        if sample_rate != 16000:
            raise ValueError(
                f"Smart Turn V3 requires 16000 Hz sample rate (got: {sample_rate})"
            )
        
        # Call parent constructor with validated sample rate
        super().__init__(sample_rate=sample_rate, params=params)

        logger.debug("Loading Smart Turn V3 model...")

        # Try to find model path if not provided
        if model_path is None:
            model_name = "smart-turn-v3.0.onnx"
            package_path = "piopiy.audio.vad.data"

            try:
                import importlib_resources as impresources

                model_path = str(impresources.files(package_path).joinpath(model_name))
            except BaseException:
                from importlib import resources as impresources

                try:
                    with impresources.path(package_path, model_name) as f:
                        model_path = str(f)
                except BaseException:
                    model_path = str(impresources.files(package_path).joinpath(model_name))

        self._model = SmartTurnV3Model(model_path, force_onnx_cpu=False)
        
        # Buffer for accumulating audio
        self._audio_buffer = np.array([], dtype=np.float32)
        self._min_audio_length = 0.5  # Minimum audio length in seconds for analysis
        
        logger.debug("Loaded Smart Turn V3 model")

    #
    # VADAnalyzer
    #

    def set_sample_rate(self, sample_rate: int):
        """Set the sample rate for audio processing.

        Args:
            sample_rate: Audio sample rate (must be 16000 Hz).

        Raises:
            ValueError: If sample rate is not 16000 Hz.
        """
        if sample_rate != 16000:
            raise ValueError(f"Smart Turn V3 requires 16000Hz sample rate (got {sample_rate}Hz)")

        super().set_sample_rate(sample_rate)

    def num_frames_required(self) -> int:
        """Get the number of audio frames required for analysis.

        Returns:
            Number of frames required (512 for 16kHz).
        """
        return 512

    def voice_confidence(self, buffer) -> float:
        """Calculate turn completion confidence for the given audio buffer.

        Args:
            buffer: Audio buffer to analyze (int16 PCM data).

        Returns:
            Turn completion confidence score between 0.0 and 1.0.
        """
        try:
            # Get sample rate from parent class
            sr = self.sample_rate
            
            # If sample rate is not set yet, use default
            if sr == 0:
                logger.warning("Sample rate not initialized, using 16000 Hz")
                sr = 16000
            
            # Convert int16 buffer to float32 in range [-1.0, 1.0]
            audio_int16 = np.frombuffer(buffer, np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0
            
            # Accumulate audio in buffer
            self._audio_buffer = np.concatenate([self._audio_buffer, audio_float32])
            
            # Only analyze if we have enough audio
            min_samples = int(self._min_audio_length * sr)
            if len(self._audio_buffer) < min_samples:
                return 0.0
            
            # Run model inference
            turn_probability = self._model(self._audio_buffer, sr)
            
            # Clear buffer after analysis
            self._audio_buffer = np.array([], dtype=np.float32)
            
            return turn_probability
            
        except Exception as e:
            logger.error(f"Error analyzing audio with Smart Turn V3: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Reset buffer on error
            self._audio_buffer = np.array([], dtype=np.float32)
            return 0.0