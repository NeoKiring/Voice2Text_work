# ディレクトリ構成

```text
Voice2Text_work/
├─ README.md
├─ run_voice2text.bat
├─ requirements.txt
├─ docs/
│  ├─ architecture.md
│  └─ development_guide.md
├─ src/
│  ├─ main.py
│  ├─ core/
│  │  ├─ config_manager.py
│  │  ├─ event_bus.py
│  │  ├─ logger.py
│  │  └─ metrics.py
│  ├─ audio/
│  │  ├─ audio_capture.py
│  │  └─ vad.py
│  ├─ transcription/
│  │  └─ engine.py
│  ├─ export/
│  │  └─ exporters.py
│  ├─ session/
│  │  ├─ session_types.py
│  │  └─ session_controller.py
│  └─ ui/
│     └─ app.py
├─ scripts/
│  └─ launch.py
└─ tests/
   ├─ test_config_manager.py
   └─ test_session_controller.py
```
