import pyautogui
import pytesseract
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import os
from pynput import mouse

# Tesseractのパスを設定（自分のインストールパスに変更）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Text Detector")
        self.root.geometry("300x100")

        self.detect_button = tk.Button(root, text="Detect Text", command=self.prepare_for_detection)
        self.detect_button.pack(pady=20)

        self.detected_text_window = None
        self.click_count_window = None
        self.click_points = []
        self.listener = None

    def prepare_for_detection(self):
        self.click_points = []
        self.show_click_count_window()
        messagebox.showinfo("Info", "Click 4 points on the screen to define the text detection area.")
        self.listener = mouse.Listener(on_click=self.on_mouse_click)
        self.listener.start()

    def show_click_count_window(self):
        if self.click_count_window:
            self.click_count_window.destroy()
        self.click_count_window = tk.Toplevel(self.root)
        self.click_count_window.title("Click Count")
        self.click_count_window.geometry("100x50+10+10")
        self.click_count_window.attributes('-topmost', True)
        self.click_count_label = tk.Label(self.click_count_window, text="Clicks: 0")
        self.click_count_label.pack(pady=10)

    def update_click_count(self):
        self.click_count_label.config(text=f"Clicks: {len(self.click_points)}")

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.click_points.append((x, y))
            self.update_click_count()
            if len(self.click_points) == 4:
                if self.click_count_window:
                    self.click_count_window.destroy()
                self.listener.stop()
                self.detect_text()

    def detect_text(self):
        # 四角形の範囲を決定
        x_coordinates = [p[0] for p in self.click_points]
        y_coordinates = [p[1] for p in self.click_points]
        left = min(x_coordinates)
        top = min(y_coordinates)
        right = max(x_coordinates)
        bottom = max(y_coordinates)

        # 指定した範囲のスクリーンショットを取得
        screenshot_path = "screenshot.png"
        screenshot = pyautogui.screenshot(region=(left, top, right-left, bottom-top))
        screenshot.save(screenshot_path)

        # OCRでテキストを検出
        text = pytesseract.image_to_string(Image.open(screenshot_path))

        # スクリーンショットファイルを削除
        os.remove(screenshot_path)

        # 検出結果を表示するウィンドウを作成
        if self.detected_text_window:
            self.detected_text_window.destroy()
        self.detected_text_window = tk.Toplevel(self.root)
        self.detected_text_window.title("Detected Text")
        text_widget = tk.Text(self.detected_text_window, wrap='word')
        text_widget.insert('1.0', text)
        text_widget.pack(expand=True, fill='both')
        # 行数に基づいてウィンドウサイズを調整
        max_chars_per_line = 70  # 1行あたりの最大文字数（適宜調整してください）
        max_lines = text.count('\n') + 1

        # 一行あたりの文字数/max_chars_per_lineを全行に行い、それらが1より大きければmax_linesにそれらの行の数だけ1を追加する
        lines = text.split('\n')
        for line in lines:
            max_lines += max(0, len(line) // max_chars_per_line)

        text_widget.config(width=max_chars_per_line, height=max_lines)

        # テキストウィジェットを更新してサイズを確定
        text_widget.update_idletasks()
        text_widget.config(state='disabled')
        width = text_widget.winfo_reqwidth() + 20
        height = text_widget.winfo_reqheight() + 20

        # ウィンドウサイズの最大値を設定
        max_width = self.root.winfo_screenwidth() - 10  # 画面幅 - マージン
        max_height = self.root.winfo_screenheight() - 10  # 画面高さ - マージン
        width = min(width, max_width)
        height = min(height, max_height)
        self.detected_text_window.geometry(f"{width}x{height}")

        # ウィンドウを一度最前面に表示し、その後通常のウィンドウに戻す
        self.detected_text_window.attributes('-topmost', True)
        self.detected_text_window.after(1000, lambda: self.detected_text_window.attributes('-topmost', False))

# GUIの設定
root = tk.Tk()
app = App(root)
root.mainloop()
