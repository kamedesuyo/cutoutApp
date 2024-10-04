import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
from rembg import remove
import subprocess
import uuid

# todo alpha_matting_foreground_threshold,alpha_matting_background_thresholdの入力

# ウィンドウのサイズを定義
WIDTH = 600
HEIGHT = 550

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.image_loaded = False
        self.image_path = None
        
        self.title("画像切り抜きアプリ")
        self.geometry(f'{WIDTH}x{HEIGHT}')
        
        self.create_widgets()
        
    def create_widgets(self):
        # 画像読み込みとクリアのボタンを配置するフレーム
        button_frame = tk.Frame(self)
        tk.Button(button_frame, text="ファイルを開く", command=self.load_image, width=10).grid(column=0, row=0)
        tk.Button(button_frame, text="クリア", command=self.clear_image, width=10).grid(column=1, row=0)
        button_frame.pack(pady=20)
        
        # 画像を表示するためのラベルフレーム
        self.label_frame = tk.LabelFrame(self, width=400, height=400, text="ここに画像をドラッグ＆ドロップ", labelanchor="n")
        self.label_frame.drop_target_register(DND_FILES)
        self.label_frame.dnd_bind('<<Drop>>', self.handle_drag_and_drop)
        self.label_frame.pack()
        
        # 切り抜き機能のボタン
        tk.Button(self, text="切り抜く", command=self.cutout).pack()
    
    def load_image(self):
        self.image_path = filedialog.askopenfilename()
        if self.image_loaded:
            self.clear_image()
        
        if self.image_path:  # ファイルが選択されたか確認
            self.display_image(self.image_path)
    
    def clear_image(self):
        if hasattr(self, 'image_label'):
            self.image_label.destroy()
            self.image_loaded = False

    def handle_drag_and_drop(self, event):
        self.image_path = str(event.data).strip("{}")  # 中括弧を削除
        self.clear_image()
        self.display_image(self.image_path)
    
    def display_image(self, path):
        try:
            image = Image.open(path)
            image.thumbnail((400, 400))
            photo_image = ImageTk.PhotoImage(image)
            self.image_label = tk.Label(self.label_frame, image=photo_image)
            self.image_label.image = photo_image  # ガーベジコレクションを防ぐために参照を保持
            self.image_label.pack()
            self.image_loaded = True
        except Exception as e:
            print(f"画像の読み込み中にエラーが発生しました: {e}")
    
    def cutout(self):
        if self.image_path:
            try:
                result_image = remove(Image.open(self.image_path))
                self.result_image = result_image.copy() # 代入ではshallowになるためcopy
                self.open_result_window(result_image)
            except Exception as e:
                print(f"切り抜き中にエラーが発生しました: {e}")
    
    def open_result_window(self, result_image):
        # subwindow
        self.result_image_window = tk.Toplevel(self)
        self.result_image_window.title("結果")
        self.result_image_window.geometry("500x600")
        self.result_image_window.grab_set()  # このウィンドウにフォーカスを設定
        
        label_frame = tk.LabelFrame(self.result_image_window, width=500, height=500,)

        result_image.thumbnail((500, 500))
        result_photo_image = ImageTk.PhotoImage(result_image)
        result_image_label = tk.Label(label_frame, image=result_photo_image)
        result_image_label.image = result_photo_image  # GC対策

        label_frame.pack(padx=0.5, pady=0.5)
        result_image_label.pack()
        
        tk.Button(self.result_image_window, text="保存", command=self.save_result_image).pack()
        tk.Button(self.result_image_window, text="保存したファイルの場所を開く", command=self.open_save_file).pack()

        self.result_image_window.protocol("WM_DELETE_WINDOW", self.result_image_window.destroy)
    
    def save_result_image(self):
        try:
            # 処理された結果の画像を "out.png" として保存
            self.result_image.save(f"./output/out-{uuid.uuid1()}.png")
            messagebox.showinfo("お知らせ", "画像を保存しました！")
        except Exception as e:
            messagebox.showerror("エラー", f"画像の保存に失敗しました: {e}")

    def open_save_file(self):
        subprocess.Popen(["explorer",r".\output"])        
        pass
if __name__ == "__main__":
    App().mainloop()