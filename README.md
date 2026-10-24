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

## Configurable alert rules (QA)

- Open **Alerts & rules / 通知とルール**, select or add a rule and edit its metric, threshold, sustained seconds, repeat cooldown, and optional exact executable name. Click **Update selected rule** and **Apply & save** to activate changes.
- Monitoring and alerts are **OFF until explicitly started/enabled**. Rules/Windows-toast preference are saved locally only on explicit Apply & save. No monitoring in the background after closing the app.
- Preset rules cover CPU/RAM/GPU/disk/VRAM (GPU/VRAM only when sensors truly exist), plus AI candidate and CPU+candidate conditions in AI-PC Monitor. Process-name observations are not proof of active AI inference or hardware failure.
- Alerts include a nonmodal in-app popup, on-screen history bounded to 200 events (not auto-saved), recovery messages, per-rule cooldowns and 10-minute snooze. No repeated alerts during snooze.
- **Windows notification/toast is optional and OFF by default**. This preview uses winotify; uninstalled QA EXEs may be blocked by Windows notification registration or user settings. Toast delivery has **NOT** been physically confirmed and needs the signed package/installer with a valid AUMID. In-app alerts work independently.
- Only local observations; no external network or cloud notification service. Unavailable sensors never count as zero. Process conditions require accessible process listing and match *exact names*, not arbitrary scripts.

No signed Store MSIX or approval is claimed; **Store release remains HOLD**.
