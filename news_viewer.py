import tkinter as tk
from tkinter import ttk, scrolledtext
from newsapi import NewsApiClient
import requests
from PIL import Image, ImageTk
from io import BytesIO
import traceback
import webbrowser

class NewsViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Просмотр новостей")
        self.root.geometry("1000x800")

        self.api = NewsApiClient(api_key='21f1746750894cf4ae69cbf3b1dc453f')
        self.images = []
        self.is_dark_theme = False

        self.style = ttk.Style()
        self.create_widgets()
        self.apply_theme()

    def create_widgets(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(control_frame, text="Категория:").pack(side='left', padx=5)
        self.category_var = tk.StringVar(value='general')
        categories = ['general', 'business', 'technology', 'sports', 'entertainment', 'science', 'health']
        category_menu = ttk.Combobox(control_frame, textvariable=self.category_var, values=categories)
        category_menu.pack(side='left', padx=5)
        category_menu.bind('<<ComboboxSelected>>', lambda e: self.update_news())

        ttk.Button(control_frame, text="Обновить", command=self.update_news).pack(side='left', padx=5)

        theme_button = ttk.Button(control_frame, text="Сменить тему", command=self.toggle_theme)
        theme_button.pack(side='right', padx=5)

        self.canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.update_news()

    def apply_theme(self):
        if self.is_dark_theme:
            bg_color = '#2b2b2b'
            fg_color = '#ffffff'
        else:
            bg_color = '#ffffff'
            fg_color = '#000000'

        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TButton', background=bg_color)
        self.style.configure('TCombobox', background=bg_color, foreground=fg_color)
        self.style.configure('TSeparator', background=fg_color)

        self.root.configure(bg=bg_color)
        self.canvas.configure(bg=bg_color)
        self.scrollable_frame.configure(style='TFrame')

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
        self.update_news()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_image(self, url):
        try:
            response = requests.get(url, timeout=5)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img = img.resize((200, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.images.append(photo)
            return photo
        except Exception as e:
            print(f"Ошибка загрузки изображения: {str(e)}")
            return None

    def create_hyperlink(self, parent, text, url):
        link = ttk.Label(parent, text=text, cursor="hand2")
        link.bind("<Button-1>", lambda e: webbrowser.open_new(url))
        if self.is_dark_theme:
            link.configure(foreground="#00ff00")
        else:
            link.configure(foreground="blue")
        return link

    def update_news(self):
        try:
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.images = []

            loading_label = ttk.Label(self.scrollable_frame, text="Загрузка новостей...")
            loading_label.pack(pady=20)
            self.root.update()

            news = self.api.get_top_headlines(
                category=self.category_var.get(),
                language='en'
            )

            loading_label.destroy()

            if news['articles']:
                for article in news['articles']:
                    news_frame = ttk.Frame(self.scrollable_frame)
                    news_frame.pack(fill='x', padx=10, pady=5)

                    image_url = article.get('urlToImage')
                    if image_url:
                        photo = self.load_image(image_url)
                        if photo:
                            image_label = ttk.Label(news_frame, image=photo)
                            image_label.pack(side='left', padx=5)

                    text_frame = ttk.Frame(news_frame)
                    text_frame.pack(side='left', fill='x', expand=True, padx=5)

                    title = article.get('title', 'Без заголовка')
                    title_label = ttk.Label(text_frame, text=title, wraplength=700,
                                          font=('Arial', 12, 'bold'))
                    title_label.pack(anchor='w')

                    description = article.get('description', 'Описание отсутствует')
                    desc_label = ttk.Label(text_frame, text=description, wraplength=700)
                    desc_label.pack(anchor='w', pady=5)

                    source = article.get('source', {}).get('name', 'Неизвестный источник')
                    published = article.get('publishedAt', '').split('T')[0]
                    url = article.get('url', '')

                    link = self.create_hyperlink(text_frame, f"Источник: {source}", url)
                    link.pack(anchor='w')

                    date_label = ttk.Label(text_frame, text=f"Дата: {published}")
                    date_label.pack(anchor='w')

                    ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', pady=10)
            else:
                ttk.Label(self.scrollable_frame,
                         text="Новости не найдены. Попробуйте другую категорию или обновите позже.").pack(pady=20)

        except Exception as e:
            error_text = f"Ошибка при загрузке новостей:\n{str(e)}\n\n"
            error_text += "Подробности ошибки:\n"
            error_text += traceback.format_exc()
            error_label = ttk.Label(self.scrollable_frame, text=error_text, wraplength=800)
            error_label.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsViewer(root)
    root.mainloop() 