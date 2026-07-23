import tkinter as tk
from tkinter import messagebox
import json
import os

class Skin:
    """Класс модели скина"""
    def __init__(self, skin_id, name, rarity, image_url=""):
        self.id = skin_id
        self.name = name
        self.rarity = rarity
        self.image_url = image_url
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rarity": self.rarity,
            "image_url": self.image_url
        }
    
    @staticmethod
    def from_dict(data):
        return Skin(data["id"], data["name"], data["rarity"], data.get("image_url", ""))

class SkinChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skin Changer")
        self.root.geometry("400x250")
        self.root.configure(bg="#1a1a2e")
        
        # Убираем стандартные элементы окна
        self.root.overrideredirect(True)
        
        # Делаем окно плавающим (поверх всех окон)
        self.root.attributes("-topmost", True)
        
        # Возможность перетаскивать окно
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.on_move)
        
        # Исходная база скинов (пример)
        self.default_skins = [
            Skin(101, "AK-47 Redline", "Rare"),
            Skin(102, "M4A4 Howl", "Epic"),
            Skin(103, "AWP Dragon Lore", "Legendary"),
            Skin(104, "Desert Eagle Blaze", "Rare"),
            Skin(105, "USP-S Kill Confirmed", "Epic"),
            Skin(106, "Glock-18 Water Elemental", "Uncommon"),
            Skin(107, "P250 Whiteout", "Common"),
            Skin(108, "Five-SeveN Case Hardened", "Rare"),
            Skin(109, "AK-47 Fire Serpent", "Legendary"),
            Skin(110, "M4A1-S Hyper Beast", "Epic"),
            Skin(111, "SSG 08 Death Strike", "Rare"),
            Skin(112, "P90 Asiimov", "Legendary")
        ]
        
        # Текущая база
        self.current_skins = [skin for skin in self.default_skins]
        
        self.setup_ui()
    
    def start_move(self, event):
        """Начало перетаскивания окна"""
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        """Перетаскивание окна"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Создание интерфейса"""
        # Заголовок с возможностью закрыть окно
        header_frame = tk.Frame(self.root, bg="#2a2a4e", height=30)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Skin Changer",
            font=("Arial", 12, "bold"),
            fg="#00d4ff",
            bg="#2a2a4e"
        )
        title_label.pack(side="left", padx=10)
        
        # Кнопка закрытия
        close_btn = tk.Button(
            header_frame,
            text="X",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="#e74c3c",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.root.destroy
        )
        close_btn.pack(side="right", padx=5, pady=2)
        
        # Основной контент
        content_frame = tk.Frame(self.root, bg="#1a1a2e", padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Поле для старого ID
        tk.Label(
            content_frame,
            text="Старый ID:",
            fg="#ff6b6b",
            bg="#1a1a2e",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_old = tk.Entry(
            content_frame,
            font=("Arial", 14),
            bg="#2d2d44",
            fg="white",
            insertbackground="white",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#00d4ff",
            highlightbackground="#2d2d44"
        )
        self.entry_old.pack(fill="x", pady=(0, 15))
        
        # Поле для нового ID
        tk.Label(
            content_frame,
            text="Новый ID:",
            fg="#51cf66",
            bg="#1a1a2e",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_new = tk.Entry(
            content_frame,
            font=("Arial", 14),
            bg="#2d2d44",
            fg="white",
            insertbackground="white",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#00d4ff",
            highlightbackground="#2d2d44"
        )
        self.entry_new.pack(fill="x", pady=(0, 20))
        
        # Кнопка замены
        self.btn_change = tk.Button(
            content_frame,
            text="Заменить скин",
            font=("Arial", 13, "bold"),
            bg="#00c853",
            fg="white",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            relief="flat",
            command=self.change_skin
        )
        self.btn_change.pack(fill="x", pady=(0, 10))
        
        # Кнопка сброса (маленькая)
        self.btn_reset = tk.Button(
            content_frame,
            text="Сбросить базу",
            font=("Arial", 10),
            bg="#d32f2f",
            fg="white",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            relief="flat",
            command=self.reset_database
        )
        self.btn_reset.pack()
        
        # Текстовое поле для вывода информации
        self.info_label = tk.Label(
            content_frame,
            text="",
            fg="#aaaaaa",
            bg="#1a1a2e",
            font=("Arial", 10),
            wraplength=350
        )
        self.info_label.pack(pady=(10, 0))
    
    def change_skin(self):
        """Логика замены ID скина"""
        old_text = self.entry_old.get().strip()
        new_text = self.entry_new.get().strip()
        
        # Проверка ввода
        if not old_text or not new_text:
            self.info_label.config(text="Ошибка: Заполните оба поля!", fg="#ff6b6b")
            return
        
        try:
            old_id = int(old_text)
            new_id = int(new_text)
        except ValueError:
            self.info_label.config(text="Ошибка: Введите числа!", fg="#ff6b6b")
            return
        
        if old_id == new_id:
            self.info_label.config(text="ID совпадают, замена не нужна", fg="#f1c40f")
            return
        
        # Проверяем существование старого ID
        old_skin = None
        for skin in self.current_skins:
            if skin.id == old_id:
                old_skin = skin
                break
        
        if not old_skin:
            self.info_label.config(text=f"Ошибка: Скин с ID {old_id} не найден!", fg="#ff6b6b")
            return
        
        # Проверяем, не занят ли новый ID
        for skin in self.current_skins:
            if skin.id == new_id:
                self.info_label.config(
                    text=f"Ошибка: ID {new_id} уже занят скином '{skin.name}'!",
                    fg="#ff6b6b"
                )
                return
        
        # Выполняем замену
        new_skin = Skin(
            skin_id=new_id,
            name=old_skin.name,
            rarity=old_skin.rarity,
            image_url=old_skin.image_url
        )
        
        # Находим индекс и заменяем
        index = self.current_skins.index(old_skin)
        self.current_skins[index] = new_skin
        
        # Очищаем поля
        self.entry_old.delete(0, tk.END)
        self.entry_new.delete(0, tk.END)
        
        self.info_label.config(
            text=f"Готово: {old_skin.name} ({old_skin.rarity}) ID {old_id} -> {new_id}",
            fg="#00c853"
        )
    
    def reset_database(self):
        """Сброс базы к исходной"""
        if messagebox.askyesno("Подтверждение", "Сбросить базу скинов?"):
            self.current_skins = [skin for skin in self.default_skins]
            self.info_label.config(text="База скинов восстановлена!", fg="#f1c40f")
            self.entry_old.delete(0, tk.END)
            self.entry_new.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = SkinChangerApp(root)
    root.mainloop()