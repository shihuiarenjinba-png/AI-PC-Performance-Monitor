# AI-PC Performance Monitor

**Independent Windows desktop app — development QA only. Not ready for sale.**

Separate from Folder Privacy Auditor, CPU-GPU Monitor and Whisper-AI.

## What it does

- Japanese / English tabbed GUI with clear **Start** and **Stop**.
- Opt-in local CPU, RAM and disk monitoring every 2 seconds; monitoring is **OFF by default**.
- CPU/RAM trend graph, memory-based process list in the backend.
- Shows possible local AI-related processes **by executable name**, such as Ollama, LM Studio or llama.cpp.
- **IMPORTANT:** Candidate process names never prove AI inference is happening. A high CPU/RAM load can be caused by games or other programs and must **not** be classified as AI usage.
- GPU load, VRAM, and CPU temperature are **UNAVAILABLE** in this edition. Do not interpret unavailable as zero.
- Explicit local JSON history save to %LOCALAPPDATA%/AIPCPerformanceMonitor/pc_load_history.json, and delete option; maximum 900 samples. No automatic disk history creation, data upload, or API usage.

## Run and test

Windows 10/11 and Python 3.12, then:

    python -m pip install -r requirements.txt
    python app.py
    python -m unittest discover -s tests -v

No Ollama installation required. No administrator privileges necessary for normal user-accessible metrics. Process list may be incomplete without elevated privileges.

## Windows artifact

GitHub Actions workflow builds a **QA_UNSIGNED Windows EXE** on feature branch pushes and runs automated tests. It does **not** bundle or load any AI model. No actual long-running GUI test, installed EXE validation, GPU sensing, WACK or Microsoft Store approval is yet complete.

**Sales / Store submission: HOLD** until signing, real hardware QA, accessibility/layout screenshots, and product identity/permissions are reviewed.

## Privacy and limitations

Only local statistics, PID and process names are inspected. No network, documents, command lines, prompts, chats, or personal file contents are read. History is written only after clicking Save; delete clears only the saved history file, not the in-memory readings. The saved JSON may include process names: keep it private.
