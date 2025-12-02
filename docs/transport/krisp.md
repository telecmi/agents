# Krisp Integration Guide 

## 1. Download the Krisp SDK and Model

Download two files:

1. The Krisp Python SDK ZIP file
   Example:

   ```
   https://xxxxxxx-xrxxx-sdks.xxxx.xxxxxxxxxxs.com/krisp-audio-sdk-python-1.4.0.zip
   ```

2. The Krisp model ZIP file
   Example:

   ```
   https://xxxxxxx-xxxx-sdks.xxxx.xxxxxxxxxxs.xxx/krisp-viva-modelsxxxxx.zip
   ```

Create a directory to store the model:

```
/home/user/xxxxx/agents/src/piopiy/audio/krisp
```

Extract both the SDK and the model into this directory. You can do it somewhere else as well.

---

## 2. Install the Krisp Python Wheel

Inside the extracted SDK directory, navigate into `dist/` and locate the wheel file that matches your `platform` and `Python` version.

For example:

```
krisp_audio-1.4.0-cp311-cp311-linux_x86_64.whl
```

Install it locally:

```
pip install krisp_audio-1.4.0-cp311-cp311-linux_x86_64.whl
```

---

## 3. Set the Model Path in .env

Add the following entry inside your `.env` file:

```
KRISP_MODEL_PATH=<path-of-the-viva-model>
```

This path must point to the `.kef` model file inside the extracted Krisp model directory, as in `telecmi.py` it is taking the path from env file.

---

## 4. Code Changes Required

### 4.1 Add `krisp_viva_filter.py`

Create a new file at:

```
/home/user/xxxxx/agents/src/piopiy/audio/filters/krisp_viva_filter.py
```

Place the Krisp Viva filter implementation inside it.
This file defines a filter class implementing the Piopiy `BaseAudioFilter` interface so it can be used by the transport.

---

### 4.2 Modified VoiceAgent (enable Krisp)

The VoiceAgent is updated to:

* Accept new parameters:

  * `enable_krisp`
  * `krisp_suppression_level`
* Create a Krisp filter only when `enable_krisp=True`
* Insert the filter into `telecmi_params` before building the TeleCMI transport

This makes the filter optional and fully configurable from the application side.

---

### 4.3 Modified telecmi.py (TeleCMI Transport)

The TeleCMI Input Transport is updated to support a generic audio filter:

* Added support for `krisp_model_path` and initialising `krisp viva filter`
* The filter is started when the transport starts
* Incoming audio frames are run through the filter before being passed to the next step
* The filter is stopped on transport stop or cancel

---

### 4.3 Modify base_transport.py (BaseTransport)

The BaseTransport is updated to support a generic audio filter:

* Added support for `enable_krisp: bool = False` and `krisp_suppression_level: int = 30`
---


## 5. Enabling Krisp When Creating the Agent

When calling `voice_agent.Action(...)`, include the new parameters:

```
await voice_agent.Action(
    stt=...,
    llm=...,
    tts=...,
    vad=True,
    allow_interruptions=True,
    interruption_strategy=MinWordsInterruptionStrategy(min_words=1),
    enable_krisp=True,
    krisp_suppression_level=30
)
```

This enables Krisp, loads the model, and passes the filter into TeleCMI for live noise suppression.
