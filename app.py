"""Standalone bilingual opt-in PC workload/AI-process candidate viewer."""
from __future__ import annotations

import queue
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

from pc_load import LocalMonitor, delete_history, history_path, save_history
from dark_theme import BG, BORDER, CARD, SOFT, MUTED, PURPLE, CYAN, TEXT, apply_theme, dark_text, header, metric

STRINGS = {
    "ja": {
        "title": "AI PC 負荷モニター（ローカル）", "start": "計測開始", "stop": "停止",
        "save": "履歴を保存", "delete": "保存履歴を削除", "toggle": "English",
        "overview": "PC負荷", "process": "ローカルAI候補", "history": "CPU / RAM 履歴",
        "cpu": "CPU使用率", "ram": "メモリ使用率", "disk": "ディスク使用率",
        "gpu": "GPU使用率", "temp": "CPU温度", "unavailable": "取得不可",
        "off": "停止中（自動収集なし）", "on": "監視中（2秒ごと）",
        "hint": "候補はプロセス名のみから推定されます。AI推論中との断定はできません。\n"
                "PC負荷が高くてもAI使用とは判定しません。ネットワーク通信なし。",
        "nothing": "該当プロセス名は見つかりません（AI不使用の証明ではありません）。",
        "saved": "ローカルに履歴を保存しました", "deleted": "保存履歴を削除しました",
        "error": "エラー", "count": "記録数",
    },
    "en": {
        "title": "AI PC Load Monitor (local only)", "start": "Start monitoring", "stop": "Stop",
        "save": "Save history", "delete": "Delete saved history", "toggle": "日本語",
        "overview": "PC load", "process": "Local AI candidates", "history": "CPU / RAM history",
        "cpu": "CPU usage", "ram": "RAM usage", "disk": "Disk usage",
        "gpu": "GPU usage", "temp": "CPU temperature", "unavailable": "Unavailable",
        "off": "Stopped (no automatic collection)", "on": "Monitoring (every 2 seconds)",
        "hint": "Candidates are matched by process name, NOT proof that AI inference is running.\n"
                "High load never implies AI usage. No network traffic.",
        "nothing": "No known process names observed (does not prove AI is absent).",
        "saved": "History saved locally", "deleted": "Saved history deleted",
        "error": "Error", "count": "Samples",
    },
}


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        apply_theme(root, accent=PURPLE)
        self.lang = "ja"
        self.monitor = LocalMonitor(Path.home(), interval=2)
        self.pending: queue.Queue[dict] = queue.Queue()
        self.monitor.on_sample = self.pending.put
        self.last = None
        root.geometry("980x700")
        root.minsize(760, 540)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.hero_title, self.hero_subtitle = header(
            root, "●  LOCAL AI / OBSERVABILITY", "AI WORKLOAD MONITOR",
            "ローカルAIの実行候補とPC負荷を確認", right="OFFLINE  •  PRIVATE")
        self.bar = ttk.Frame(root, style="Toolbar.TFrame", padding=(14, 10))
        self.bar.pack(fill="x")
        self.buttons = {}
        for key, action in (("start", self.start), ("stop", self.stop),
                            ("save", self.save), ("delete", self.delete)):
            button = ttk.Button(self.bar, command=action, style=("Primary.TButton" if key == "start" else "Quiet.TButton" if key == "delete" else "TButton"))
            button.pack(side="left", padx=4)
            self.buttons[key] = button
        self.buttons["toggle"] = ttk.Button(self.bar, command=self.change_language, style="Quiet.TButton")
        self.buttons["toggle"].pack(side="right", padx=4)

        self.state = tk.StringVar()
        ttk.Label(root, textvariable=self.state, style="Status.TLabel", padding=(19, 4)).pack(anchor="w")
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=8)
        self.pages = {key: ttk.Frame(self.tabs, style="Panel.TFrame", padding=15)
                      for key in ("overview", "process", "history")}
        for page in self.pages.values():
            self.tabs.add(page)
        self.value_labels = {}
        self.name_labels = {}
        cards = ttk.Frame(self.pages["overview"], style="Panel.TFrame")
        cards.pack(fill="both", expand=True)
        for col in range(3):
            cards.columnconfigure(col, weight=1, uniform="metrics")
        for idx, key in enumerate(("cpu", "ram", "gpu", "disk", "temp", "count")):
            tile, name, value = metric(cards, key, accent=key in {"cpu", "gpu", "count"})
            tile.grid(row=idx // 3, column=idx % 3, sticky="nsew", padx=5, pady=5)
            self.name_labels[key] = name
            self.value_labels[key] = value
        self.notice = ttk.Label(self.pages["overview"], wraplength=800,
                                justify="left", style="PanelText.TLabel")
        self.notice.pack(anchor="w", pady=(12, 0))
        self.candidates = tk.Text(self.pages["process"], wrap="none", state="disabled")
        dark_text(self.candidates)
        self.candidates.pack(fill="both", expand=True)
        self.chart = tk.Canvas(self.pages["history"], background=SOFT,
                               highlightthickness=1, highlightbackground=BORDER)
        self.chart.pack(fill="both", expand=True)
        self.chart.bind("<Configure>", lambda e: self.draw_chart())
        self.translate()
        root.after(250, self.poll)

    def w(self, key):
        return STRINGS[self.lang][key]

    def translate(self):
        self.root.title(self.w("title"))
        self.hero_subtitle.configure(text=("ローカルAI候補・PC負荷を安全に監視" if self.lang == "ja" else "Local AI candidates and PC workload  /  NO CLOUD"))
        for key, button in self.buttons.items():
            button.configure(text=self.w(key))
        for key, page in self.pages.items():
            self.tabs.tab(page, text=self.w(key))
        for key, name in self.name_labels.items():
            name.configure(text=self.w(key))
        self.notice.configure(text=self.w("hint"))
        self.refresh()

    def change_language(self):
        self.lang = "en" if self.lang == "ja" else "ja"
        self.translate()

    def start(self):
        self.monitor.start()
        self.refresh()

    def stop(self):
        self.monitor.stop()
        self.refresh()

    def refresh(self):
        active = bool(self.monitor.worker and self.monitor.worker.is_alive())
        self.state.set(self.w("on") if active else self.w("off"))
        self.buttons["start"].configure(state="disabled" if active else "normal")
        self.buttons["stop"].configure(state="normal" if active else "disabled")
        d = self.last or {}
        for key, field in (("cpu", "cpu_percent"), ("ram", "ram_percent"),
                           ("disk", "disk_percent"), ("gpu", "gpu_percent")):
            value = d.get(field)
            self.value_labels[key].configure(
                text=(f"{value:.1f} %" if isinstance(value, (float, int))
                      else self.w("unavailable")))
        self.value_labels["temp"].configure(text=self.w("unavailable"))
        self.value_labels["count"].configure(text=str(len(self.monitor.history)))
        detected = d.get("local_ai_related_process_candidates", [])
        rows = ([f"PID {item['pid']} — {item['name']} (candidate only)"
                 for item in detected] if detected else [self.w("nothing")])
        self.candidates.configure(state="normal")
        self.candidates.delete("1.0", "end")
        self.candidates.insert("1.0", "\n".join(rows))
        self.candidates.configure(state="disabled")
        self.draw_chart()

    def draw_chart(self):
        self.chart.delete("all")
        width = max(self.chart.winfo_width(), 100)
        height = max(self.chart.winfo_height(), 100)
        left, top, right, bottom = 50, 18, width - 20, height - 35
        self.chart.create_rectangle(left, top, right, bottom, outline=BORDER)
        for level in (25, 50, 75):
            y = bottom - (bottom - top) * level / 100
            self.chart.create_line(left, y, right, y, fill=BORDER, dash=(3, 7))
        history = list(self.monitor.history)[-120:]
        if not history:
            return
        for field, color in (("cpu_percent", CYAN), ("ram_percent", PURPLE)):
            pts = []
            for idx, sample in enumerate(history):
                val = sample.get(field)
                if isinstance(val, (int, float)):
                    x = left + (right - left) * idx / max(1, len(history) - 1)
                    y = bottom - (bottom - top) * max(0, min(100, val)) / 100
                    pts.extend((x, y))
            if len(pts) >= 4:
                self.chart.create_line(*pts, fill=color, width=2)
            elif len(pts) == 2:
                self.chart.create_oval(pts[0] - 2, pts[1] - 2, pts[0] + 2, pts[1] + 2,
                                       fill=color)
        self.chart.create_text(left + 80, height - 15, text="CPU", fill=CYAN)
        self.chart.create_text(left + 170, height - 15, text="RAM", fill=PURPLE)
        self.chart.create_text(left - 20, top, text="100%", fill=MUTED)
        self.chart.create_text(left - 20, bottom, text="0%", fill=MUTED)

    def poll(self):
        changed = False
        try:
            while True:
                self.last = self.pending.get_nowait()
                changed = True
        except queue.Empty:
            pass
        if changed:
            self.refresh()
        if self.monitor.errors:
            self.stop()
            messagebox.showerror(self.w("error"), self.monitor.errors.popleft())
        self.root.after(250, self.poll)

    def save(self):
        try:
            path = save_history(list(self.monitor.history))
            messagebox.showinfo(self.w("save"), self.w("saved") + "\n" + str(path))
        except (OSError, ValueError) as exc:
            messagebox.showerror(self.w("error"), str(exc))

    def delete(self):
        try:
            delete_history()
            messagebox.showinfo(self.w("delete"), self.w("deleted"))
        except (OSError, ValueError) as exc:
            messagebox.showerror(self.w("error"), str(exc))

    def close(self):
        self.monitor.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
