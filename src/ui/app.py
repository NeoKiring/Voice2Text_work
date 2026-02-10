from __future__ import annotations

import customtkinter as ctk

from src.session.session_controller import SessionController


class Voice2TextApp(ctk.CTk):
    def __init__(self, controller: SessionController) -> None:
        super().__init__()
        self.controller = controller
        self.title("Voice2Text")
        self.geometry("800x500")

        self.start_btn = ctk.CTkButton(self, text="開始", command=self._on_start)
        self.start_btn.pack(pady=8)

        self.stop_btn = ctk.CTkButton(self, text="停止", command=self._on_stop)
        self.stop_btn.pack(pady=8)

        self.status_label = ctk.CTkLabel(self, text="状態: idle")
        self.status_label.pack(pady=8)

        self.output = ctk.CTkTextbox(self, width=760, height=360)
        self.output.pack(padx=16, pady=8)

        controller.event_bus.subscribe("session.started", self._on_started)
        controller.event_bus.subscribe("session.stopped", self._on_stopped)
        controller.event_bus.subscribe("transcript.segment", self._on_segment)

    def _on_start(self) -> None:
        self.controller.start()

    def _on_stop(self) -> None:
        self.controller.stop()

    def _on_started(self, event) -> None:
        self.after(0, lambda: self.status_label.configure(text=f"状態: running ({event.payload['session_id']})"))

    def _on_stopped(self, event) -> None:
        files = "\n".join(event.payload.get("files", []))
        self.after(0, lambda: self.status_label.configure(text="状態: stopped"))
        self.after(0, lambda: self.output.insert("end", f"\n[保存完了]\n{files}\n"))

    def _on_segment(self, event) -> None:
        self.after(0, lambda: self.output.insert("end", event.payload["text"] + "\n"))
