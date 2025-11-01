import customtkinter as ctk
import pandas as pd
import qrcode
import os
import configparser
from datetime import datetime
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
from tkinter import simpledialog, scrolledtext
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class DataManager:
    """Менеджер для работы с данными и Excel файлами"""

    def __init__(self):
        self.data_dir = "data"
        self.orders_file = os.path.join(self.data_dir, "orders.xlsx")
        self.inventory_file = os.path.join(self.data_dir, "inventory.xlsx")
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Создание директории данных если не существует"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_orders(self):
        """Загрузка заказов из Excel"""
        try:
            if os.path.exists(self.orders_file):
                df = pd.read_excel(self.orders_file)
                return df
            else:
                return self.create_new_orders_file()
        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")
            return self.create_new_orders_file()

    def create_new_orders_file(self):
        """Создание нового файла заказов"""
        df = pd.DataFrame(columns=[
            'ID', 'Дата', 'ФИО', 'Возраст', 'Заказ', 'Комментарий',
            'Сумма', 'Оплата', 'Сдача'
        ])
        self.save_orders(df)
        return df

    def save_orders(self, df):
        """Сохранение заказов в Excel"""
        try:
            df.to_excel(self.orders_file, index=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения заказов: {e}")
            return False

    def add_order(self, order_data):
        """Добавление нового заказа"""
        try:
            df = self.load_orders()
            new_order_df = pd.DataFrame([order_data])
            df = pd.concat([df, new_order_df], ignore_index=True)
            return self.save_orders(df)
        except Exception as e:
            print(f"Ошибка добавления заказа: {e}")
            return False

    def load_inventory(self):
        """Загрузка остатков из Excel"""
        try:
            if os.path.exists(self.inventory_file):
                df = pd.read_excel(self.inventory_file)
                return df
            else:
                return self.create_new_inventory_file()
        except Exception as e:
            print(f"Ошибка загрузки остатков: {e}")
            return self.create_new_inventory_file()

    def create_new_inventory_file(self):
        """Создание нового файла остатков"""
        inventory_data = {
            'Продукт': [
                'Тесто', 'Сыр', 'Томатный соус', 'Пепперони', 'Ветчина',
                'Бекон', 'Грибы', 'Перец', 'Лук', 'Оливки', 'Ананасы',
                'Кола', 'Фанта', 'Спрайт', 'Вода', 'Сок'
            ],
            'Количество': [
                100, 20.0, 15.0, 8.0, 10.0, 6.0, 12.0, 15.0, 10.0, 8.0, 7.0,
                50, 50, 50, 50, 30
            ],
            'Единица_измерения': [
                'шт', 'кг', 'л', 'кг', 'кг', 'кг', 'кг', 'кг', 'кг', 'кг', 'кг',
                'шт', 'шт', 'шт', 'шт', 'шт'
            ],
            'Минимальный_запас': [
                10, 2.0, 2.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 0.5, 0.5,
                10, 10, 10, 10, 5
            ]
        }

        df = pd.DataFrame(inventory_data)
        self.save_inventory(df)
        return df

    def save_inventory(self, df):
        """Сохранение остатков в Excel"""
        try:
            df.to_excel(self.inventory_file, index=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения остатков: {e}")
            return False

    def update_inventory(self, order_items):
        """Обновление остатков на основе заказа"""
        try:
            df = self.load_inventory()

            for item in order_items:
                item_lower = item.lower()

                # Учет пицц
                if "пицца" in item_lower:
                    self._decrement_product(df, "Тесто", 1)
                    self._decrement_product(df, "Сыр", 0.2)
                    self._decrement_product(df, "Томатный соус", 0.1)

                # Учет начинок
                toppings_mapping = {
                    'пепперони': 'Пепперони',
                    'ветчина': 'Ветчина',
                    'бекон': 'Бекон',
                    'грибы': 'Грибы',
                    'перец': 'Перец',
                    'лук': 'Лук',
                    'оливки': 'Оливки',
                    'ананасы': 'Ананасы'
                }

                for topping_key, product_name in toppings_mapping.items():
                    if topping_key in item_lower:
                        self._decrement_product(df, product_name, 0.05)

                # Учет напитков
                drinks_mapping = {
                    'кола': 'Кола',
                    'фанта': 'Фанта',
                    'спрайт': 'Спрайт',
                    'вода': 'Вода',
                    'сок': 'Сок'
                }

                for drink_key, product_name in drinks_mapping.items():
                    if drink_key in item_lower:
                        self._decrement_product(df, product_name, 1)

            # Проверка минимальных запасов
            low_stock = df[df['Количество'] <= df['Минимальный_запас']]
            if not low_stock.empty:
                low_stock_products = low_stock['Продукт'].tolist()
                messagebox.showwarning(
                    "Внимание",
                    f"Низкий запас продуктов:\n{', '.join(low_stock_products)}"
                )

            return self.save_inventory(df)

        except Exception as e:
            print(f"Ошибка обновления остатков: {e}")
            return False

    def _decrement_product(self, df, product_name, amount):
        """Уменьшение количества продукта"""
        mask = df['Продукт'] == product_name
        if mask.any():
            current_value = df.loc[mask, 'Количество'].iloc[0]
            if current_value >= amount:
                df.loc[mask, 'Количество'] = current_value - amount


class ConfigManager:
    """Менеджер конфигурационных файлов"""

    def __init__(self):
        self.config_dir = "config"
        self.ensure_config_directory()

    def ensure_config_directory(self):
        """Создание директории конфигов если не существует"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def load_receipt_config(self):
        """Загрузка настроек чека"""
        config = configparser.ConfigParser()
        try:
            config.read('config/receipt_config.txt', encoding='utf-8')
            if not config.sections():
                raise FileNotFoundError
            return config
        except Exception as e:
            print(f"Ошибка загрузки настроек чека: {e}")
            return self.create_default_receipt_config()

    def create_default_receipt_config(self):
        """Создание настроек чека по умолчанию"""
        config = configparser.ConfigParser()
        config['Чек'] = {
            'Название_компании': 'Pizza Maker 🍕',
            'ИНН': '123456789012',
            'Адрес': 'г. Москва, ул. Пушкина, д. 1',
            'Телефон': '+7 (495) 123-45-67',
            'Сайт': 'https://pizza-maker.ru',
            'НДС': '20%'
        }
        config['QR'] = {
            'Ссылка': 'https://genius-school.kuzstu.ru/pizza-maker'
        }
        return config

    def load_images_config(self):
        """Загрузка конфигурации изображений"""
        images_config = {"Пиццы": {}, "Напитки": {}}
        try:
            config = configparser.ConfigParser()
            config.read('config/images_config.txt', encoding='utf-8')

            if 'Пиццы' in config:
                for pizza, image_path in config['Пиццы'].items():
                    images_config["Пиццы"][pizza] = image_path

            if 'Напитки' in config:
                for drink, image_path in config['Напитки'].items():
                    images_config["Напитки"][drink] = image_path

        except Exception as e:
            print(f"Ошибка загрузки конфигурации изображений: {e}")

        return images_config

    def load_discounts_config(self):
        """Загрузка конфигурации скидок"""
        discounts = {
            "напитки": {},
            "пиццы_взрослые": {},
            "пиццы_детские": {}
        }
        try:
            config = configparser.ConfigParser()
            config.read('config/discounts_config.txt', encoding='utf-8')

            if 'Скидки_напитки' in config:
                for volume, discount in config['Скидки_напитки'].items():
                    discounts["напитки"][volume] = float(discount)

            if 'Скидки_пиццы' in config:
                for size, multiplier in config['Скидки_пиццы'].items():
                    discounts["пиццы_взрослые"][size] = float(multiplier)

            if 'Скидки_детские' in config:
                for size, multiplier in config['Скидки_детские'].items():
                    discounts["пиццы_детские"][size] = float(multiplier)

        except Exception as e:
            print(f"Ошибка загрузки конфигурации скидок: {e}")
            discounts = {
                "напитки": {"0.33л": 0.0, "0.5л": 5.0, "1л": 10.0, "1.5л": 15.0, "2л": 20.0},
                "пиццы_взрослые": {"Маленькая": 0.7, "Средняя": 0.85, "Большая": 1.0},
                "пиццы_детские": {"Маленькая": 0.75, "Средняя": 1.0, "Большая": 1.2}
            }

        return discounts

    def load_menu_config(self, menu_file):
        """Загрузка меню из файла"""
        menu = {"Пиццы": {}, "Напитки": {}}
        try:
            config = configparser.ConfigParser()
            config.read(f'config/{menu_file}', encoding='utf-8')

            if 'Пиццы' in config:
                for pizza, value in config['Пиццы'].items():
                    try:
                        price, size, ingredients = value.split('|')
                        menu["Пиццы"][pizza.replace('_', ' ')] = {
                            "цена": int(price),
                            "размер": size,
                            "ингредиенты": ingredients
                        }
                    except ValueError as e:
                        print(f"Ошибка парсинга пиццы {pizza}: {e}")

            if 'Напитки' in config:
                for drink, value in config['Напитки'].items():
                    try:
                        price, volume = value.split('|')
                        menu["Напитки"][drink] = {"цена": int(price), "объем": volume}
                    except ValueError as e:
                        print(f"Ошибка парсинга напитка {drink}: {e}")

            return menu
        except Exception as e:
            print(f"Ошибка загрузки меню {menu_file}: {e}")
            return self.create_default_menu(menu_file)

    def create_default_menu(self, menu_file):
        """Создание меню по умолчанию"""
        menu = {"Пиццы": {}, "Напитки": {}}

        if "adult" in menu_file:
            menu["Пиццы"] = {
                "Маргарита": {"цена": 450, "размер": "Большая", "ингредиенты": "Томатный соус, моцарелла, базилик"},
                "Пепперони": {"цена": 550, "размер": "Большая", "ингредиенты": "Томатный соус, пепперони, моцарелла"},
                "Гавайская": {"цена": 500, "размер": "Большая",
                              "ингредиенты": "Томатный соус, ветчина, ананасы, моцарелла"},
                "Четыре сыра": {"цена": 600, "размер": "Большая",
                                "ингредиенты": "Моцарелла, горгонзола, пармезан, рикотта"},
                "Мясная": {"цена": 650, "размер": "Большая",
                           "ингредиенты": "Томатный соус, пепперони, ветчина, бекон, моцарелла"},
                "Вегетарианская": {"цена": 480, "размер": "Большая",
                                   "ингредиенты": "Томатный соус, перец, грибы, оливки, лук, моцарелла"},
                "Кастомная": {"цена": 400, "размер": "Средняя", "ингредиенты": "Выберите начинки самостоятельно"}
            }
            menu["Напитки"] = {
                "Кола": {"цена": 150, "объем": "0.5л"},
                "Фанта": {"цена": 150, "объем": "0.5л"},
                "Спрайт": {"цена": 150, "объем": "0.5л"},
                "Вода": {"цена": 100, "объем": "0.5л"},
                "Сок": {"цена": 180, "объем": "0.5л"}
            }
        else:
            menu["Пиццы"] = {
                "Маргарита": {"цена": 350, "размер": "Средняя", "ингредиенты": "Томатный соус, моцарелла, базилик"},
                "Пепперони": {"цена": 400, "размер": "Средняя", "ингредиенты": "Томатный соус, пепперони, моцарелла"},
                "Гавайская": {"цена": 380, "размер": "Средняя",
                              "ингредиенты": "Томатный соус, ветчина, ананасы, моцарелла"},
                "Четыре сыра": {"цена": 450, "размер": "Средняя",
                                "ингредиенты": "Моцарелла, горгонзола, пармезан, рикотта"},
                "Кастомная": {"цена": 300, "размер": "Маленькая", "ингредиенты": "Выберите начинки самостоятельно"}
            }
            menu["Напитки"] = {
                "Кола": {"цена": 120, "объем": "0.33л"},
                "Фанта": {"цена": 120, "объем": "0.33л"},
                "Спрайт": {"цена": 120, "объем": "0.33л"},
                "Вода": {"цена": 80, "объем": "0.33л"},
                "Сок": {"цена": 150, "объем": "0.33л"}
            }

        return menu

    def load_toppings(self):
        """Загрузка начинок"""
        toppings = {}
        try:
            with open('config/toppings.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        topping, price = line.split('=')
                        toppings[topping] = int(price)
            return toppings
        except FileNotFoundError:
            print("Файл начинок не найден, создание по умолчанию")
            return self.create_default_toppings()

    def create_default_toppings(self):
        """Создание начинок по умолчанию"""
        return {
            'Пепперони': 80,
            'Ветчина': 70,
            'Бекон': 90,
            'Грибы': 50,
            'Перец': 40,
            'Лук': 30,
            'Оливки': 45,
            'Ананасы': 60,
            'Маслины': 45,
            'Помидоры': 40,
            'Кукуруза': 35,
            'Моцарелла': 55,
            'Пармезан': 65
        }

    def save_receipt_config(self, config_data):
        """Сохранение настроек чека"""
        try:
            config = configparser.ConfigParser()
            config['Чек'] = config_data['receipt']
            config['QR'] = config_data['qr']

            with open('config/receipt_config.txt', 'w', encoding='utf-8') as f:
                config.write(f)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения настроек чека: {e}")
            return False

    def save_menu_config(self, menu_data, menu_file):
        """Сохранение меню в файл"""
        try:
            config = configparser.ConfigParser()

            # Пиццы
            config['Пиццы'] = {}
            for pizza, info in menu_data["Пиццы"].items():
                config['Пиццы'][pizza.replace(' ', '_')] = f"{info['цена']}|{info['размер']}|{info['ингредиенты']}"

            # Напитки
            config['Напитки'] = {}
            for drink, info in menu_data["Напитки"].items():
                config['Напитки'][drink] = f"{info['цена']}|{info['объем']}"

            with open(f'config/{menu_file}', 'w', encoding='utf-8') as f:
                config.write(f)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения меню: {e}")
            return False

    def save_toppings(self, toppings_data):
        """Сохранение начинок"""
        try:
            with open('config/toppings.txt', 'w', encoding='utf-8') as f:
                for topping, price in toppings_data.items():
                    f.write(f"{topping}={price}\n")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения начинок: {e}")
            return False

    def save_discounts(self, discounts_data):
        """Сохранение настроек скидок"""
        try:
            with open('config/discounts_config.txt', 'w', encoding='utf-8') as f:
                for volume, discount in discounts_data["напитки"].items():
                    f.write(f"{volume}={discount}\n")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения скидок: {e}")
            return False


class ImageManager:
    """Менеджер для работы с изображениями"""

    def __init__(self):
        self.image_cache = {}
        self.default_image = self.create_default_image()

    def create_default_image(self):
        """Создание изображения по умолчанию"""
        img = Image.new('RGB', (200, 150), color='lightgray')
        return ImageTk.PhotoImage(img)

    def load_image(self, image_path, size=(200, 150)):
        """Загрузка и масштабирование изображения"""
        try:
            if image_path in self.image_cache:
                return self.image_cache[image_path]

            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_cache[image_path] = photo
                return photo
            else:
                print(f"Изображение не найдено: {image_path}")
                return self.default_image
        except Exception as e:
            print(f"Ошибка загрузки изображения {image_path}: {e}")
            return self.default_image


class AnalyticsManager:
    """Менеджер аналитики"""

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def load_orders_data(self):
        """Загрузка данных о заказах"""
        return self.data_manager.load_orders()

    def get_popular_orders(self, top_n=10):
        """Получение самых популярных заказов"""
        df = self.load_orders_data()
        if df.empty:
            return []

        all_orders = []
        for orders in df['Заказ']:
            if pd.notna(orders):
                items = str(orders).split('; ')
                all_orders.extend(items)

        order_counts = Counter(all_orders)
        return order_counts.most_common(top_n)

    def get_age_distribution(self):
        """Получение распределения по возрастам"""
        df = self.load_orders_data()
        if df.empty:
            return pd.Series()

        return df['Возраст'].value_counts().sort_index()

    def get_sales_statistics(self):
        """Получение статистики продаж"""
        df = self.load_orders_data()
        if df.empty:
            return {
                'total_orders': 0,
                'total_revenue': 0,
                'avg_order_value': 0,
                'most_popular_time': 'Нет данных'
            }

        total_orders = len(df)
        total_revenue = df['Сумма'].sum()
        avg_order_value = df['Сумма'].mean()

        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'most_popular_time': '12:00'
        }


class PizzaMakerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Pizza Maker 🍕")
        self.geometry("1200x800")
        self.resizable(True, True)

        # Инициализация менеджеров
        self.data_manager = DataManager()
        self.config_manager = ConfigManager()
        self.image_manager = ImageManager()
        self.analytics_manager = AnalyticsManager(self.data_manager)

        # Загрузка конфигурации
        self.load_configuration()

        # Данные пользователя
        self.user_data = {}
        self.current_order = []
        self.total_amount = 0
        self.user_comment = ""

        self.create_welcome_frame()

    def load_configuration(self):
        """Загрузка всей конфигурации"""
        try:
            self.receipt_config = self.config_manager.load_receipt_config()
            self.images_config = self.config_manager.load_images_config()
            self.discounts_config = self.config_manager.load_discounts_config()
            self.menu_adult = self.config_manager.load_menu_config('menu_adult.txt')
            self.menu_minor = self.config_manager.load_menu_config('menu_minor.txt')
            self.toppings = self.config_manager.load_toppings()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки конфигурации: {e}")

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_welcome_frame(self):
        self.clear_frame()

        # Заголовок
        title_label = ctk.CTkLabel(self,
                                   text="🍕 Pizza Maker",
                                   font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=40)

        # Фрейм для ввода данных
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=20, padx=50, fill="both", expand=True)

        ctk.CTkLabel(input_frame,
                     text="Добро пожаловать!",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Поле ФИО
        ctk.CTkLabel(input_frame, text="ФИО:",
                     font=ctk.CTkFont(size=14)).pack(pady=5)
        self.fio_entry = ctk.CTkEntry(input_frame,
                                      placeholder_text="Введите ваше ФИО",
                                      width=300,
                                      height=35)
        self.fio_entry.pack(pady=10)

        # Поле возраста
        ctk.CTkLabel(input_frame, text="Возраст:",
                     font=ctk.CTkFont(size=14)).pack(pady=5)
        self.age_entry = ctk.CTkEntry(input_frame,
                                      placeholder_text="Введите ваш возраст",
                                      width=300,
                                      height=35)
        self.age_entry.pack(pady=10)

        # Кнопки
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(pady=30)

        continue_btn = ctk.CTkButton(button_frame,
                                     text="Продолжить",
                                     command=self.process_user_info,
                                     height=40,
                                     font=ctk.CTkFont(size=16))
        continue_btn.pack(side="left", padx=10)

        settings_btn = ctk.CTkButton(button_frame,
                                     text="Настройки",
                                     command=self.show_settings,
                                     height=40,
                                     font=ctk.CTkFont(size=16),
                                     fg_color="gray",
                                     hover_color="#4a4a4a")
        settings_btn.pack(side="left", padx=10)

    def process_user_info(self):
        fio = self.fio_entry.get().strip()
        age_text = self.age_entry.get().strip()

        if not fio:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ФИО")
            return

        try:
            age = int(age_text)
            if age <= 0:
                messagebox.showerror(
                    "Ошибка", "Возраст должен быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "Пожалуйста, введите корректный возраст")
            return

        self.user_data = {"fio": fio, "age": age}
        self.create_menu_frame()

    def create_menu_frame(self):
        self.clear_frame()

        is_adult = self.user_data["age"] >= 18
        menu = self.menu_adult if is_adult else self.menu_minor
        pizza_discounts = self.discounts_config["пиццы_взрослые"] if is_adult else self.discounts_config[
            "пиццы_детские"]

        # Заголовок
        welcome_text = f"Здравствуйте, {self.user_data['fio']}!"
        if is_adult:
            welcome_text += " Вам доступно взрослое меню 🍕"
        else:
            welcome_text += " Добро пожаловать! 🍕"

        title_label = ctk.CTkLabel(self,
                                   text=welcome_text,
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=20)

        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Фрейм меню
        menu_frame = ctk.CTkFrame(main_frame)
        menu_frame.pack(side="left",
                        padx=10,
                        pady=10,
                        fill="both",
                        expand=True)

        # Фрейм корзины
        cart_frame = ctk.CTkFrame(main_frame, width=300)
        cart_frame.pack(side="right", padx=10, pady=10, fill="y")

        # Вкладки
        tabview = ctk.CTkTabview(menu_frame)
        tabview.pack(pady=10, padx=10, fill="both", expand=True)

        tab_pizzas = tabview.add("🍕 Пиццы")
        tab_drinks = tabview.add("🥤 Напитки")

        # Отображение пицц с изображениями и выбором размера
        for pizza, info in menu["Пиццы"].items():
            pizza_frame = ctk.CTkFrame(tab_pizzas)
            pizza_frame.pack(pady=10, padx=10, fill="x")

            # Верхняя часть: изображение и информация
            top_frame = ctk.CTkFrame(pizza_frame)
            top_frame.pack(fill="x", pady=5)

            # Изображение пиццы
            image_path = self.images_config["Пиццы"].get(pizza, "")
            pizza_image = self.image_manager.load_image(image_path, size=(120, 90))

            image_label = ctk.CTkLabel(top_frame, image=pizza_image, text="")
            image_label.pack(side="left", padx=10)

            # Информация о пицце
            info_frame = ctk.CTkFrame(top_frame)
            info_frame.pack(side="left", fill="x", expand=True, padx=10)

            pizza_text = f"{pizza} - {info['цена']} руб. ({info['размер']})"
            ctk.CTkLabel(info_frame,
                         text=pizza_text,
                         font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

            ctk.CTkLabel(info_frame,
                         text=info['ингредиенты'],
                         font=ctk.CTkFont(size=12),
                         text_color="gray").pack(anchor="w")

            # Нижняя часть: выбор размера и кнопки
            bottom_frame = ctk.CTkFrame(pizza_frame)
            bottom_frame.pack(fill="x", pady=5)

            # Выбор размера
            size_frame = ctk.CTkFrame(bottom_frame)
            size_frame.pack(side="left", padx=10)

            ctk.CTkLabel(size_frame, text="Размер:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            size_var = ctk.StringVar(value=info['размер'])

            size_options = list(pizza_discounts.keys())
            size_menu = ctk.CTkOptionMenu(size_frame, variable=size_var, values=size_options, width=120)
            size_menu.pack(side="left", padx=5)

            # Отображение цены с учетом размера
            price_label = ctk.CTkLabel(size_frame, text="", font=ctk.CTkFont(size=12, weight="bold"))
            price_label.pack(side="left", padx=10)

            def update_price(p=info['цена'], s=size_var, l=price_label, d=pizza_discounts):
                size = s.get()
                multiplier = d.get(size, 1.0)
                new_price = int(p * multiplier)
                l.configure(text=f"{new_price} руб.")

            size_var.trace('w', lambda *args: update_price())
            update_price()  # Initial update

            # Кнопки
            button_frame = ctk.CTkFrame(bottom_frame)
            button_frame.pack(side="right", padx=10)

            # Кнопка комментария для конкретной пиццы
            comment_btn = ctk.CTkButton(button_frame,
                                        text="💬",
                                        command=lambda p=pizza: self.add_item_comment_dialog(p),
                                        width=40,
                                        height=30,
                                        fg_color="orange",
                                        hover_color="#cc5500")
            comment_btn.pack(side="left", padx=2)

            add_btn = ctk.CTkButton(button_frame,
                                    text="Добавить",
                                    command=lambda p=pizza, sz=size_var, base=info['цена'], d=pizza_discounts:
                                    self.add_pizza_with_size(p, sz, base, d),
                                    width=100)
            add_btn.pack(side="left", padx=2)

            if pizza == "Кастомная":
                custom_btn = ctk.CTkButton(
                    button_frame,
                    text="Создать свою",
                    command=self.create_custom_pizza_dialog,
                    width=100,
                    fg_color="green",
                    hover_color="#006400")
                custom_btn.pack(side="left", padx=2)

        # Отображение напитков с выбором объема и учетом скидок
        for drink, info in menu["Напитки"].items():
            drink_frame = ctk.CTkFrame(tab_drinks)
            drink_frame.pack(pady=10, padx=10, fill="x")

            # Верхняя часть: изображение и информация
            top_frame = ctk.CTkFrame(drink_frame)
            top_frame.pack(fill="x", pady=5)

            # Изображение напитка
            image_path = self.images_config["Напитки"].get(drink, "")
            drink_image = self.image_manager.load_image(image_path, size=(80, 80))

            image_label = ctk.CTkLabel(top_frame, image=drink_image, text="")
            image_label.pack(side="left", padx=10)

            # Информация о напитке
            info_frame = ctk.CTkFrame(top_frame)
            info_frame.pack(side="left", fill="x", expand=True, padx=10)

            drink_text = f"{drink} - {info['цена']} руб. ({info['объем']})"
            ctk.CTkLabel(info_frame,
                         text=drink_text,
                         font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

            # Выбор объема с отображением скидки
            volume_frame = ctk.CTkFrame(info_frame)
            volume_frame.pack(anchor="w", pady=5)

            ctk.CTkLabel(volume_frame, text="Объем:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            volume_var = ctk.StringVar(value=info['объем'])

            # Создаем опции с отображением скидки
            volume_options = []
            for volume in ["0.33л", "0.5л", "1л", "1.5л", "2л"]:
                discount = self.discounts_config["напитки"].get(volume, 0.0)
                if discount > 0:
                    volume_options.append(f"{volume} (-{discount}%)")
                else:
                    volume_options.append(volume)

            volume_menu = ctk.CTkOptionMenu(volume_frame, variable=volume_var, values=volume_options, width=100)
            volume_menu.pack(side="left", padx=5)

            # Отображение цены с учетом скидки
            drink_price_label = ctk.CTkLabel(volume_frame, text="", font=ctk.CTkFont(size=12, weight="bold"))
            drink_price_label.pack(side="left", padx=10)

            def update_drink_price(p=info['цена'], v=volume_var, l=drink_price_label,
                                   d=self.discounts_config["напитки"]):
                volume_text = v.get()
                volume = volume_text.split(' ')[0]  # Извлекаем чистый объем
                discount = d.get(volume, 0.0)
                final_price = int(p * (1 - discount / 100))
                l.configure(text=f"{final_price} руб.")

            volume_var.trace('w', lambda *args: update_drink_price())
            update_drink_price()  # Initial update

            # Кнопки для напитков
            drink_button_frame = ctk.CTkFrame(drink_frame)
            drink_button_frame.pack(anchor="e", pady=5)

            # Кнопка комментария для напитка
            drink_comment_btn = ctk.CTkButton(drink_button_frame,
                                              text="💬",
                                              command=lambda d=drink: self.add_item_comment_dialog(d),
                                              width=40,
                                              height=30,
                                              fg_color="orange",
                                              hover_color="#cc5500")
            drink_comment_btn.pack(side="left", padx=2)

            add_btn = ctk.CTkButton(drink_button_frame,
                                    text="Добавить",
                                    command=lambda d=drink, price=info['цена'], vol=volume_var:
                                    self.add_drink_with_volume(d, price, vol),
                                    width=100)
            add_btn.pack(side="left", padx=2)

        # Поле для общего комментария к заказу
        comment_frame = ctk.CTkFrame(menu_frame)
        comment_frame.pack(pady=10, padx=10, fill="x")

        comment_btn = ctk.CTkButton(comment_frame,
                                    text="💬 Добавить общий комментарий к заказу",
                                    command=self.add_general_comment_dialog,
                                    height=35,
                                    fg_color="blue",
                                    hover_color="#00008b")
        comment_btn.pack(pady=5)

        # Отображение текущего комментария
        self.comment_label = ctk.CTkLabel(comment_frame,
                                          text="",
                                          font=ctk.CTkFont(size=12),
                                          text_color="gray",
                                          wraplength=400)
        self.comment_label.pack(pady=5)

        if self.user_comment:
            self.comment_label.configure(text=f"Комментарий: {self.user_comment}")

        # Корзина
        ctk.CTkLabel(cart_frame,
                     text="🛒 Ваш заказ",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.cart_textbox = ctk.CTkTextbox(cart_frame, height=300, width=280)
        self.cart_textbox.pack(pady=10, padx=10, fill="both", expand=True)

        self.update_cart_display()

        ctk.CTkLabel(cart_frame,
                     text=f"Итого: {self.total_amount} руб.",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        checkout_btn = ctk.CTkButton(cart_frame,
                                     text="Оформить заказ",
                                     command=self.checkout,
                                     height=40,
                                     font=ctk.CTkFont(size=16))
        checkout_btn.pack(pady=10)

        clear_btn = ctk.CTkButton(cart_frame,
                                  text="Очистить корзину",
                                  command=self.clear_cart,
                                  height=30,
                                  fg_color="gray",
                                  hover_color="#4a4a4a")
        clear_btn.pack(pady=5)

    def add_item_comment_dialog(self, item_name):
        """Диалог для добавления комментария к конкретному товару"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Комментарий к {item_name}")
        dialog.geometry("400x250")
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog,
                     text=f"Добавить комментарий к {item_name}:",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        comment_text = scrolledtext.ScrolledText(dialog, width=40, height=6, font=("Arial", 12))
        comment_text.pack(pady=10, padx=20, fill="both", expand=True)

        # Проверяем, есть ли уже комментарий для этого товара
        existing_comment = ""
        for order_item in self.current_order:
            if order_item['item'].startswith(item_name) and 'comment' in order_item:
                existing_comment = order_item['comment']
                break

        comment_text.insert("1.0", existing_comment)

        def save_comment():
            comment = comment_text.get("1.0", "end-1c").strip()

            # Находим товар в заказе и добавляем комментарий
            for order_item in self.current_order:
                if order_item['item'].startswith(item_name):
                    if comment:
                        order_item['comment'] = comment
                        # Обновляем отображение в корзине
                        order_item['item'] = f"{item_name.split('(')[0].strip()} ({order_item['item'].split('(')[1]} 💬"
                    else:
                        # Удаляем комментарий если пустой
                        if 'comment' in order_item:
                            del order_item['comment']
                        # Возвращаем оригинальное название
                        if '💬' in order_item['item']:
                            order_item['item'] = order_item['item'].replace('💬', '').strip()

                    self.update_cart_display()
                    break

            dialog.destroy()
            if comment:
                messagebox.showinfo("Успех", f"Комментарий добавлен к {item_name}")

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame,
                      text="Сохранить",
                      command=save_comment,
                      height=35).pack(side="left", padx=5)

        ctk.CTkButton(button_frame,
                      text="Отмена",
                      command=dialog.destroy,
                      height=35,
                      fg_color="gray").pack(side="left", padx=5)

    def add_general_comment_dialog(self):
        """Диалог для добавления общего комментария к заказу"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Общий комментарий к заказу")
        dialog.geometry("500x300")
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog,
                     text="Введите общий комментарий к заказу:",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        comment_text = scrolledtext.ScrolledText(dialog, width=50, height=10, font=("Arial", 12))
        comment_text.pack(pady=10, padx=20, fill="both", expand=True)
        comment_text.insert("1.0", self.user_comment)

        def save_comment():
            self.user_comment = comment_text.get("1.0", "end-1c").strip()
            if self.user_comment:
                self.comment_label.configure(text=f"Комментарий: {self.user_comment}")
            else:
                self.comment_label.configure(text="")
            dialog.destroy()

        ctk.CTkButton(dialog,
                      text="Сохранить",
                      command=save_comment,
                      height=40).pack(pady=10)

    def add_pizza_with_size(self, pizza, size_var, base_price, discounts):
        """Добавление пиццы с выбранным размером"""
        size = size_var.get()
        multiplier = discounts.get(size, 1.0)
        price = int(base_price * multiplier)
        item_name = f"{pizza} ({size})"

        # Проверяем, есть ли уже эта пицца в заказе с комментарием
        for order_item in self.current_order:
            if order_item['item'].startswith(pizza) and 'comment' in order_item:
                item_name = f"{pizza} ({size}) 💬"
                order_item['item'] = item_name
                order_item['price'] = price
                self.total_amount = sum(item['price'] for item in self.current_order)
                self.update_cart_display()
                messagebox.showinfo("Успех", f"{pizza} обновлена в корзине!")
                return

        # Если пиццы еще нет в заказе, добавляем новую
        self.current_order.append({"item": item_name, "price": price, "quantity": 1})
        self.total_amount += price
        self.update_cart_display()
        messagebox.showinfo("Успех", f"{item_name} добавлена в корзину!")

    def add_drink_with_volume(self, drink, base_price, volume_var):
        """Добавление напитка с выбранным объемом и учетом скидки"""
        volume_text = volume_var.get()
        volume = volume_text.split(' ')[0]  # Извлекаем чистый объем

        discount = self.discounts_config["напитки"].get(volume, 0.0)
        final_price = int(base_price * (1 - discount / 100))

        item_name = f"{drink} ({volume})"
        if discount > 0:
            item_name += f" [СКИДКА {discount}%]"

        # Проверяем, есть ли уже этот напиток в заказе с комментарием
        for order_item in self.current_order:
            if order_item['item'].startswith(drink) and 'comment' in order_item:
                item_name = f"{drink} ({volume}) 💬"
                if discount > 0:
                    item_name += f" [СКИДКА {discount}%]"
                order_item['item'] = item_name
                order_item['price'] = final_price
                self.total_amount = sum(item['price'] for item in self.current_order)
                self.update_cart_display()
                messagebox.showinfo("Успех", f"{drink} обновлен в корзине!")
                return

        # Если напитка еще нет в заказе, добавляем новый
        self.current_order.append({"item": item_name, "price": final_price, "quantity": 1})
        self.total_amount += final_price
        self.update_cart_display()
        messagebox.showinfo("Успех", f"{item_name} добавлен в корзину!")

    def update_cart_display(self):
        self.cart_textbox.delete("1.0", "end")
        if not self.current_order:
            self.cart_textbox.insert("1.0", "Корзина пуста")
            return

        for i, order_item in enumerate(self.current_order, 1):
            item_text = f"{i}. {order_item['item']} - {order_item['price']} руб."
            # Добавляем комментарий если есть
            if 'comment' in order_item:
                item_text += f"\n   💬 {order_item['comment']}"
            self.cart_textbox.insert("end", item_text + "\n\n")

    def clear_cart(self):
        self.current_order = []
        self.total_amount = 0
        self.user_comment = ""
        self.comment_label.configure(text="")
        self.update_cart_display()

    def create_custom_pizza_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Создание кастомной пиццы")
        dialog.geometry("500x600")
        dialog.resizable(False, False)

        is_adult = self.user_data["age"] >= 18
        base_price = 400 if is_adult else 300
        selected_toppings = []
        current_price = base_price

        def update_price():
            nonlocal current_price
            current_price = base_price + sum(self.toppings[top]
                                             for top in selected_toppings)
            price_label.configure(
                text=f"Текущая стоимость: {current_price} руб.")

        ctk.CTkLabel(dialog,
                     text="Выберите начинки:",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        price_label = ctk.CTkLabel(
            dialog,
            text=f"Текущая стоимость: {current_price} руб.",
            font=ctk.CTkFont(size=14))
        price_label.pack(pady=5)

        scroll_frame = ctk.CTkScrollableFrame(dialog)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        topping_vars = {}

        for topping, price in self.toppings.items():
            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(pady=2, fill="x")

            var = ctk.BooleanVar()
            topping_vars[topping] = var

            def make_callback(t):

                def callback():
                    if var.get():
                        if t not in selected_toppings:
                            selected_toppings.append(t)
                    else:
                        if t in selected_toppings:
                            selected_toppings.remove(t)
                    update_price()

                return callback

            chk = ctk.CTkCheckBox(frame,
                                  text=f"{topping} (+{price} руб.)",
                                  variable=var,
                                  command=make_callback(topping))
            chk.pack(side="left", padx=10, pady=5)

        def add_custom_pizza():
            if not selected_toppings:
                messagebox.showwarning("Предупреждение",
                                       "Выберите хотя бы одну начинку!")
                return

            description = f"Кастомная пицца с: {', '.join(selected_toppings)}"
            self.current_order.append({
                "item": description,
                "price": current_price
            })
            self.total_amount += current_price
            self.update_cart_display()
            dialog.destroy()
            messagebox.showinfo("Успех",
                                "Кастомная пицца добавлена в корзину!")

        ctk.CTkButton(dialog,
                      text="Добавить в корзину",
                      command=add_custom_pizza,
                      height=40).pack(pady=20)

    def checkout(self):
        if not self.current_order:
            messagebox.showwarning("Предупреждение", "Корзина пуста!")
            return

        self.create_payment_frame()

    def create_payment_frame(self):
        self.clear_frame()

        title_label = ctk.CTkLabel(self,
                                   text="Оформление заказа",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        order_frame = ctk.CTkFrame(self)
        order_frame.pack(pady=10, padx=50, fill="x")

        ctk.CTkLabel(order_frame,
                     text="Ваш заказ:",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        order_text = ctk.CTkTextbox(order_frame, height=150)
        order_text.pack(pady=10, padx=10, fill="x")

        for item in self.current_order:
            order_text.insert("end",
                              f"• {item['item']} - {item['price']} руб.\n")
            if 'comment' in item:
                order_text.insert("end", f"   💬 {item['comment']}\n")

        # Показываем общий комментарий если есть
        if self.user_comment:
            order_text.insert("end", f"\n📝 Общий комментарий: {self.user_comment}\n")

        order_text.configure(state="disabled")

        ctk.CTkLabel(order_frame,
                     text=f"Итого: {self.total_amount} руб.",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        payment_frame = ctk.CTkFrame(self)
        payment_frame.pack(pady=20, padx=50, fill="x")

        ctk.CTkLabel(payment_frame,
                     text="Способ оплаты:",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.payment_var = ctk.StringVar(value="card")

        card_btn = ctk.CTkRadioButton(payment_frame,
                                      text="💳 Карта (без сдачи)",
                                      variable=self.payment_var,
                                      value="card")
        card_btn.pack(pady=5)

        cash_btn = ctk.CTkRadioButton(payment_frame,
                                      text="💵 Наличные",
                                      variable=self.payment_var,
                                      value="cash")
        cash_btn.pack(pady=5)

        self.cash_frame = ctk.CTkFrame(payment_frame)

        ctk.CTkLabel(self.cash_frame, text="Внесенная сумма:").pack(pady=5)
        self.cash_entry = ctk.CTkEntry(self.cash_frame,
                                       placeholder_text="Введите сумму")
        self.cash_entry.pack(pady=5)

        def on_payment_change():
            if self.payment_var.get() == "cash":
                self.cash_frame.pack(pady=10)
            else:
                self.cash_frame.pack_forget()

        card_btn.configure(command=on_payment_change)
        cash_btn.configure(command=on_payment_change)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame,
                      text="Назад",
                      command=self.create_menu_frame,
                      width=120,
                      height=40).pack(side="left", padx=10)

        ctk.CTkButton(button_frame,
                      text="Оплатить",
                      command=self.process_payment,
                      width=120,
                      height=40,
                      fg_color="green",
                      hover_color="#006400").pack(side="left", padx=10)

    def process_payment(self):
        payment_method = self.payment_var.get()
        change = 0

        if payment_method == "cash":
            try:
                cash_amount = int(self.cash_entry.get())
                if cash_amount < self.total_amount:
                    messagebox.showerror(
                        "Ошибка",
                        f"Недостаточно средств! Нужно еще {self.total_amount - cash_amount} руб."
                    )
                    return
                change = cash_amount - self.total_amount
                payment_text = "Наличные"
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную сумму!")
                return
        else:
            payment_text = "Карта"

        receipt_id = self.generate_receipt(payment_text, change)
        self.show_receipt_frame(receipt_id, payment_text, change)

    def generate_receipt(self, payment_method, change):
        receipt_id = datetime.now().strftime("%Y%m%d%H%M%S")
        order_items = []

        # Собираем информацию о заказе с комментариями
        for item in self.current_order:
            item_info = item['item']
            if 'comment' in item:
                item_info += f" (комментарий: {item['comment']})"
            order_items.append(item_info)

        # Сохранение в Excel
        order_data = {
            'ID': receipt_id,
            'Дата': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            'ФИО': self.user_data["fio"],
            'Возраст': self.user_data["age"],
            'Заказ': '; '.join(order_items),
            'Комментарий': self.user_comment,
            'Сумма': self.total_amount,
            'Оплата': payment_method,
            'Сдача': change
        }

        if self.data_manager.add_order(order_data):
            print("Заказ сохранен в Excel")
        else:
            print("Ошибка сохранения заказа")

        # Обновление остатков
        order_item_names = [item['item'] for item in self.current_order]
        self.data_manager.update_inventory(order_item_names)

        # Генерация QR-кода
        self.generate_qr_code(receipt_id)

        return receipt_id

    def generate_qr_code(self, receipt_id):
        try:
            qr_link = self.receipt_config['QR']['Ссылка']
            qr_data = f"Чек №: {receipt_id}\n"
            qr_data += f"Сумма: {self.total_amount} руб.\n"
            qr_data += f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            qr_data += f"Сайт: {qr_link}"

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            if not os.path.exists('qrcodes'):
                os.makedirs('qrcodes')
            img.save(f"qrcodes/receipt_{receipt_id}.png")

        except Exception as e:
            print(f"Ошибка при генерации QR-кода: {e}")

    def generate_pdf_receipt(self, receipt_id, payment_method, change):
        """Генерация чека в формате PDF по ФЗ-54"""
        try:
            pdf_filename = f"receipt_{receipt_id}.pdf"
            if not os.path.exists('receipts'):
                os.makedirs('receipts')
            pdf_path = os.path.join('receipts', pdf_filename)

            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter

            company_name = self.receipt_config['Чек']['Название_компании']
            inn = self.receipt_config['Чек']['ИНН']
            address = self.receipt_config['Чек']['Адрес']
            vat_rate = self.receipt_config['Чек']['НДС']

            y_position = height - 80

            # КАССОВЫЙ ЧЕК (ФЗ-54)
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(width / 2, y_position, "КАССОВЫЙ ЧЕК")
            y_position -= 30

            # Организация
            c.setFont("Helvetica-Bold", 11)
            c.drawString(100, y_position, company_name)
            y_position -= 18

            c.setFont("Helvetica", 9)
            c.drawString(100, y_position, f"ИНН: {inn}")
            y_position -= 15
            c.drawString(100, y_position, f"Адрес: {address}")
            y_position -= 15
            c.drawString(100, y_position, "СНО: УСН")
            y_position -= 25

            # Линия
            c.line(80, y_position, width - 80, y_position)
            y_position -= 20

            # Дата и смена
            c.setFont("Helvetica", 9)
            receipt_date = datetime.now()
            c.drawString(100, y_position, f"Дата: {receipt_date.strftime('%d.%m.%Y %H:%M:%S')}")
            y_position -= 15
            c.drawString(100, y_position, f"Кассир: {self.user_data.get('fio', 'Администратор')}")
            y_position -= 15
            c.drawString(100, y_position, f"Смена №: 1")
            y_position -= 15
            c.drawString(100, y_position, f"Чек №: {receipt_id}")
            y_position -= 25

            # Линия
            c.line(80, y_position, width - 80, y_position)
            y_position -= 20

            # ТОВАРЫ
            c.setFont("Helvetica-Bold", 10)
            c.drawString(100, y_position, "ТОВАРЫ:")
            y_position -= 18

            c.setFont("Helvetica", 8)
            vat_amount = 0
            for item in self.current_order:
                item_name = item['item']
                quantity = item.get('quantity', 1)
                price = item['price']
                total = price * quantity
                item_vat = int(total * 20 / 120)
                vat_amount += item_vat

                # Название товара
                c.drawString(100, y_position, item_name)
                y_position -= 12

                # Комментарий к товару если есть
                if 'comment' in item:
                    c.drawString(110, y_position, f"Комментарий: {item['comment']}")
                    y_position -= 12

                # Количество x Цена = Сумма
                c.drawString(110, y_position, f"{quantity} x {price}.00 = {total}.00")
                y_position -= 12
                # НДС 20%
                c.drawString(110, y_position, f"НДС 20%: {item_vat}.00")
                y_position -= 18

            # Общий комментарий если есть
            if self.user_comment:
                y_position -= 10
                c.setFont("Helvetica-Bold", 9)
                c.drawString(100, y_position, "Общий комментарий клиента:")
                y_position -= 12
                c.setFont("Helvetica", 8)
                # Разбиваем длинный комментарий на строки
                comment_lines = []
                words = self.user_comment.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) <= 50:
                        current_line += word + " "
                    else:
                        comment_lines.append(current_line)
                        current_line = word + " "
                if current_line:
                    comment_lines.append(current_line)

                for line in comment_lines:
                    c.drawString(100, y_position, line)
                    y_position -= 12

            # Линия
            c.line(80, y_position, width - 80, y_position)
            y_position -= 20

            # ИТОГО
            c.setFont("Helvetica-Bold", 11)
            c.drawString(100, y_position, f"ИТОГО: {self.total_amount}.00 руб")
            y_position -= 18

            # НДС
            c.setFont("Helvetica", 9)
            c.drawString(100, y_position, f"в т.ч. НДС 20%: {vat_amount}.00 руб")
            y_position -= 20

            # Форма оплаты
            c.setFont("Helvetica-Bold", 9)
            if payment_method == "Наличные":
                c.drawString(100, y_position, f"НАЛИЧНЫМИ: {self.total_amount}.00 руб")
                y_position -= 15
                if change > 0:
                    c.drawString(100, y_position, f"Сдача: {change}.00 руб")
                    y_position -= 15
            else:
                c.drawString(100, y_position, f"БЕЗНАЛИЧНЫМИ: {self.total_amount}.00 руб")
                y_position -= 15

            y_position -= 10
            c.line(80, y_position, width - 80, y_position)
            y_position -= 20

            # Фискальная информация
            c.setFont("Helvetica", 8)
            c.drawString(100, y_position, f"РН ККТ: 0000{inn[:10]}")
            y_position -= 12
            c.drawString(100, y_position, f"ЗН ККТ: 00000000{inn[:6]}")
            y_position -= 12
            c.drawString(100, y_position, f"ФН: 9999{inn[:8]}")
            y_position -= 12
            c.drawString(100, y_position, f"ФД: {receipt_id}")
            y_position -= 12
            fiscal_sign = int(receipt_id[-8:]) if len(receipt_id) >= 8 else int(receipt_id)
            c.drawString(100, y_position, f"ФП: {fiscal_sign}")
            y_position -= 20

            # QR-код
            qr_image_path = f"qrcodes/receipt_{receipt_id}.png"
            if os.path.exists(qr_image_path):
                c.drawImage(qr_image_path, 180, 50, width=150, height=150)

            c.save()
            return pdf_path

        except Exception as e:
            print(f"Ошибка при генерации PDF: {e}")
            return None

    def show_receipt_frame(self, receipt_id, payment_method, change):
        self.clear_frame()

        # Генерация PDF чека
        pdf_file = self.generate_pdf_receipt(receipt_id, payment_method, change)

        title_label = ctk.CTkLabel(self,
                                   text="Заказ оформлен! 🎉",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        receipt_frame = ctk.CTkFrame(self)
        receipt_frame.pack(pady=10, padx=50, fill="both", expand=True)

        # Формирование чека с настройками
        company_name = self.receipt_config['Чек']['Название_компании']
        inn = self.receipt_config['Чек']['ИНН']
        address = self.receipt_config['Чек']['Адрес']
        phone = self.receipt_config['Чек']['Телефон']
        vat = self.receipt_config['Чек']['НДС']

        receipt_text = f"""{company_name}
ИНН: {inn}
Адрес: {address}
Телефон: {phone}

ЧЕК №: {receipt_id}
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
Клиент: {self.user_data['fio']}
Возраст: {self.user_data['age']}

ЗАКАЗ:
"""
        for item in self.current_order:
            receipt_text += f"• {item['item']} - {item['price']} руб.\n"
            if 'comment' in item:
                receipt_text += f"  💬 {item['comment']}\n"

        # Добавляем общий комментарий если есть
        if self.user_comment:
            receipt_text += f"\n📝 Общий комментарий: {self.user_comment}\n"

        receipt_text += f"\nИТОГО: {self.total_amount} руб."
        receipt_text += f"\nНДС: {vat}"
        receipt_text += f"\nОплата: {payment_method}"

        if payment_method == "Наличные":
            receipt_text += f"\nВнесено: {self.total_amount + change} руб."
            receipt_text += f"\nСдача: {change} руб."

        receipt_text += f"\n\nСпасибо за заказ! 🍕"
        receipt_text += f"\n\nPDF чек сохранен: {pdf_file}"

        receipt_display = ctk.CTkTextbox(receipt_frame,
                                         font=ctk.CTkFont(family="Courier", size=12))
        receipt_display.pack(pady=20, padx=20, fill="both", expand=True)
        receipt_display.insert("1.0", receipt_text)
        receipt_display.configure(state="disabled")

        # Кнопки для чека
        receipt_actions_frame = ctk.CTkFrame(self)
        receipt_actions_frame.pack(pady=10)

        ctk.CTkLabel(receipt_actions_frame,
                     text="Действия с чеком:",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

        receipt_btns_frame = ctk.CTkFrame(receipt_actions_frame)
        receipt_btns_frame.pack(pady=5)

        ctk.CTkButton(receipt_btns_frame,
                      text="📧 Отправить",
                      command=lambda: self.send_receipt(pdf_file),
                      width=120,
                      height=35,
                      fg_color="blue",
                      hover_color="#00008b").pack(side="left", padx=5)

        ctk.CTkButton(receipt_btns_frame,
                      text="💾 Скачать PDF",
                      command=lambda: self.download_receipt(pdf_file),
                      width=120,
                      height=35,
                      fg_color="purple",
                      hover_color="#4b0082").pack(side="left", padx=5)

        ctk.CTkButton(receipt_btns_frame,
                      text="🖨️ Печать",
                      command=lambda: self.print_receipt(pdf_file),
                      width=120,
                      height=35,
                      fg_color="orange",
                      hover_color="#cc5500").pack(side="left", padx=5)

        # Основные кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame,
                      text="Новый заказ",
                      command=self.restart_app,
                      width=150,
                      height=40,
                      fg_color="green",
                      hover_color="#006400").pack(side="left", padx=10)

        ctk.CTkButton(button_frame,
                      text="Выход",
                      command=self.quit,
                      width=150,
                      height=40,
                      fg_color="red",
                      hover_color="#8b0000").pack(side="left", padx=10)

    def send_receipt(self, pdf_file):
        """Отправка чека по email"""
        email = simpledialog.askstring("Отправка чека", "Введите email:")
        if email:
            messagebox.showinfo("Успех", f"Чек отправлен на {email}\n(Демо: функция email не настроена)")

    def download_receipt(self, pdf_file):
        """Сохранение чека"""
        if pdf_file and os.path.exists(pdf_file):
            messagebox.showinfo("Успех", f"PDF чек сохранен: {pdf_file}")
        else:
            messagebox.showerror("Ошибка", "PDF файл не найден!")

    def print_receipt(self, pdf_file):
        """Печать чека"""
        if pdf_file and os.path.exists(pdf_file):
            try:
                if os.name == 'posix':  # Linux/Mac
                    os.system(f"lpr {pdf_file}")
                elif os.name == 'nt':  # Windows
                    os.startfile(pdf_file, "print")
                messagebox.showinfo("Успех", "Чек отправлен на печать!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка печати: {e}")
        else:
            messagebox.showerror("Ошибка", "PDF файл не найден!")

    def show_settings(self):
        """Окно настроек с защитой паролем"""
        password = simpledialog.askstring("Вход в настройки",
                                          "Введите пароль:",
                                          show='*')
        if password == "123":
            SettingsWindow(self)
        elif password is not None:
            messagebox.showerror("Ошибка", "Неверный пароль!")

    def restart_app(self):
        self.user_data = {}
        self.current_order = []
        self.total_amount = 0
        self.user_comment = ""
        self.load_configuration()
        self.create_welcome_frame()


# Класс SettingsWindow остается без изменений (как в предыдущем коде)
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config_manager = parent.config_manager

        self.title("Настройки Pizza Maker")
        self.geometry("900x700")
        self.resizable(True, True)

        self.create_widgets()
        self.load_current_settings()

    def create_widgets(self):
        # Вкладки настроек
        tabview = ctk.CTkTabview(self)
        tabview.pack(pady=10, padx=10, fill="both", expand=True)

        tab_receipt = tabview.add("Чек")
        tab_menu_adult = tabview.add("Меню Взрослое")
        tab_menu_minor = tabview.add("Меню Детское")
        tab_toppings = tabview.add("Начинки")
        tab_discounts = tabview.add("Скидки")
        tab_analytics = tabview.add("Аналитика")

        self.create_receipt_tab(tab_receipt)
        self.create_menu_tab(tab_menu_adult, "adult")
        self.create_menu_tab(tab_menu_minor, "minor")
        self.create_toppings_tab(tab_toppings)
        self.create_discounts_tab(tab_discounts)
        self.create_analytics_tab(tab_analytics)

        # Кнопки
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame,
                      text="Сохранить",
                      command=self.save_all_settings,
                      width=120,
                      height=40).pack(side="left", padx=10)

        ctk.CTkButton(button_frame,
                      text="Отмена",
                      command=self.destroy,
                      width=120,
                      height=40,
                      fg_color="gray",
                      hover_color="#4a4a4a").pack(side="left", padx=10)

    def create_receipt_tab(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.receipt_entries = {}
        fields = [("Название_компании", "Название компании"), ("ИНН", "ИНН"),
                  ("Адрес", "Адрес"), ("Телефон", "Телефон"), ("Сайт", "Сайт"),
                  ("НДС", "НДС (%)")]

        for key, label in fields:
            ctk.CTkLabel(scroll_frame,
                         text=label,
                         font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                               pady=(10, 5))
            entry = ctk.CTkEntry(scroll_frame, width=400)
            entry.pack(anchor="w", fill="x", pady=(0, 10))
            self.receipt_entries[key] = entry

        ctk.CTkLabel(scroll_frame,
                     text="QR Ссылка",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                           pady=(10, 5))
        self.qr_entry = ctk.CTkEntry(scroll_frame, width=400)
        self.qr_entry.pack(anchor="w", fill="x", pady=(0, 10))

    def create_menu_tab(self, parent, menu_type):
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        if menu_type == "adult":
            menu_data = self.parent.menu_adult
            self.menu_adult_entries = {"Пиццы": {}, "Напитки": {}}
            current_entries = self.menu_adult_entries
        else:
            menu_data = self.parent.menu_minor
            self.menu_minor_entries = {"Пиццы": {}, "Напитки": {}}
            current_entries = self.menu_minor_entries

        # Пиццы
        ctk.CTkLabel(scroll_frame,
                     text="ПИЦЦЫ",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(10, 5))

        for pizza, info in menu_data["Пиццы"].items():
            pizza_frame = ctk.CTkFrame(scroll_frame)
            pizza_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(pizza_frame,
                         text=pizza,
                         font=ctk.CTkFont(weight="bold")).pack(anchor="w")

            entry_frame = ctk.CTkFrame(pizza_frame)
            entry_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(entry_frame, text="Цена:").pack(side="left", padx=5)
            price_entry = ctk.CTkEntry(entry_frame, width=80)
            price_entry.insert(0, str(info["цена"]))
            price_entry.pack(side="left", padx=5)

            ctk.CTkLabel(entry_frame, text="Размер:").pack(side="left", padx=5)
            size_entry = ctk.CTkEntry(entry_frame, width=100)
            size_entry.insert(0, info["размер"])
            size_entry.pack(side="left", padx=5)

            ctk.CTkLabel(entry_frame, text="Ингредиенты:").pack(side="left", padx=5)
            ingredients_entry = ctk.CTkEntry(entry_frame, width=200)
            ingredients_entry.insert(0, info["ингредиенты"])
            ingredients_entry.pack(side="left", padx=5)

            current_entries["Пиццы"][pizza] = {
                "цена": price_entry,
                "размер": size_entry,
                "ингредиенты": ingredients_entry
            }

        # Напитки
        ctk.CTkLabel(scroll_frame,
                     text="НАПИТКИ",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(20, 5))

        for drink, info in menu_data["Напитки"].items():
            drink_frame = ctk.CTkFrame(scroll_frame)
            drink_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(drink_frame,
                         text=drink,
                         font=ctk.CTkFont(weight="bold")).pack(anchor="w")

            entry_frame = ctk.CTkFrame(drink_frame)
            entry_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(entry_frame, text="Цена:").pack(side="left", padx=5)
            price_entry = ctk.CTkEntry(entry_frame, width=80)
            price_entry.insert(0, str(info["цена"]))
            price_entry.pack(side="left", padx=5)

            ctk.CTkLabel(entry_frame, text="Объем:").pack(side="left", padx=5)
            volume_entry = ctk.CTkEntry(entry_frame, width=100)
            volume_entry.insert(0, info["объем"])
            volume_entry.pack(side="left", padx=5)

            current_entries["Напитки"][drink] = {
                "цена": price_entry,
                "объем": volume_entry
            }

    def create_toppings_tab(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.topping_entries = {}

        for topping, price in self.parent.toppings.items():
            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(fill="x", pady=2)

            ctk.CTkLabel(frame, text=topping, width=150).pack(side="left", padx=10)
            price_entry = ctk.CTkEntry(frame, width=100)
            price_entry.insert(0, str(price))
            price_entry.pack(side="left", padx=10)

            self.topping_entries[topping] = price_entry

    def create_discounts_tab(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.discount_entries = {}

        ctk.CTkLabel(scroll_frame,
                     text="Настройка скидок для объемов напитков",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=10)

        ctk.CTkLabel(scroll_frame,
                     text="Укажите процент скидки для каждого объема:",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=5)

        volumes = ["0.33л", "0.5л", "1л", "1.5л", "2л"]

        for volume in volumes:
            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(fill="x", pady=2)

            ctk.CTkLabel(frame, text=volume, width=100).pack(side="left", padx=10)
            discount_entry = ctk.CTkEntry(frame, width=100, placeholder_text="0.0")
            discount_entry.insert(0, str(self.parent.discounts_config["напитки"].get(volume, 0.0)))
            discount_entry.pack(side="left", padx=10)
            ctk.CTkLabel(frame, text="%").pack(side="left", padx=5)

            self.discount_entries[volume] = discount_entry

    def create_analytics_tab(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Статистика
        stats = self.parent.analytics_manager.get_sales_statistics()

        stats_frame = ctk.CTkFrame(scroll_frame)
        stats_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(stats_frame,
                     text="Статистика продаж",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        stats_text = f"""
        Всего заказов: {stats['total_orders']}
        Общая выручка: {stats['total_revenue']:.2f} руб.
        Средний чек: {stats['avg_order_value']:.2f} руб.
        Популярное время: {stats['most_popular_time']}
        """

        stats_label = ctk.CTkLabel(stats_frame, text=stats_text, justify="left")
        stats_label.pack(pady=10)

        # Кнопки для генерации графиков
        graphs_frame = ctk.CTkFrame(scroll_frame)
        graphs_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(graphs_frame,
                     text="Аналитические графики",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        ctk.CTkButton(graphs_frame,
                      text="📊 Популярные заказы",
                      command=self.show_popular_orders_chart,
                      width=200).pack(pady=5)

        ctk.CTkButton(graphs_frame,
                      text="👥 Распределение по возрастам",
                      command=self.show_age_distribution_chart,
                      width=200).pack(pady=5)

        ctk.CTkButton(graphs_frame,
                      text="💰 Статистика продаж",
                      command=self.show_sales_chart,
                      width=200).pack(pady=5)

    def show_popular_orders_chart(self):
        """График популярных заказов"""
        popular_orders = self.parent.analytics_manager.get_popular_orders(10)

        if not popular_orders:
            messagebox.showinfo("Информация", "Нет данных для построения графика")
            return

        items, counts = zip(*popular_orders)

        plt.figure(figsize=(12, 8))
        bars = plt.barh(items, counts, color='skyblue')
        plt.xlabel('Количество заказов')
        plt.title('Топ-10 самых популярных заказов')
        plt.gca().invert_yaxis()

        # Добавляем значения на столбцы
        for bar, count in zip(bars, counts):
            plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                     f'{count}', ha='left', va='center')

        plt.tight_layout()
        plt.show()

    def show_age_distribution_chart(self):
        """График распределения по возрастам"""
        age_distribution = self.parent.analytics_manager.get_age_distribution()

        if age_distribution.empty:
            messagebox.showinfo("Информация", "Нет данных для построения графика")
            return

        plt.figure(figsize=(12, 8))
        age_distribution.plot(kind='bar', color='lightcoral')
        plt.xlabel('Возраст')
        plt.ylabel('Количество заказов')
        plt.title('Распределение заказов по возрастам')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_sales_chart(self):
        """График статистики продаж"""
        df = self.parent.analytics_manager.load_orders_data()

        if df.empty:
            messagebox.showinfo("Информация", "Нет данных для построения графика")
            return

        # Анализ по дням недели
        df['Дата'] = pd.to_datetime(df['Дата'])
        df['День недели'] = df['Дата'].dt.day_name()

        # Перевод на русский
        days_translation = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }
        df['День недели'] = df['День недели'].map(days_translation)

        daily_sales = df.groupby('День недели')['Сумма'].sum()
        daily_orders = df.groupby('День недели')['Сумма'].count()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # График выручки по дням
        daily_sales.plot(kind='bar', ax=ax1, color='gold')
        ax1.set_title('Выручка по дням недели')
        ax1.set_ylabel('Выручка (руб)')
        ax1.tick_params(axis='x', rotation=45)

        # График количества заказов по дням
        daily_orders.plot(kind='bar', ax=ax2, color='lightgreen')
        ax2.set_title('Количество заказов по дням недели')
        ax2.set_ylabel('Количество заказов')
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()

    def load_current_settings(self):
        """Загрузка текущих настроек в поля"""
        try:
            # Настройки чека
            for key, entry in self.receipt_entries.items():
                entry.delete(0, "end")
                entry.insert(0, self.parent.receipt_config['Чек'][key])

            self.qr_entry.delete(0, "end")
            self.qr_entry.insert(0, self.parent.receipt_config['QR']['Ссылка'])

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки настроек: {e}")

    def save_all_settings(self):
        """Сохранение всех настроек"""
        try:
            # Сохранение настроек чека
            receipt_data = {}
            for key, entry in self.receipt_entries.items():
                receipt_data[key] = entry.get()

            qr_data = {'Ссылка': self.qr_entry.get()}

            self.config_manager.save_receipt_config({
                'receipt': receipt_data,
                'qr': qr_data
            })

            # Сохранение меню взрослое
            adult_menu = {"Пиццы": {}, "Напитки": {}}
            for pizza, entries in self.menu_adult_entries["Пиццы"].items():
                adult_menu["Пиццы"][pizza] = {
                    "цена": int(entries["цена"].get()),
                    "размер": entries["размер"].get(),
                    "ингредиенты": entries["ингредиенты"].get()
                }

            for drink, entries in self.menu_adult_entries["Напитки"].items():
                adult_menu["Напитки"][drink] = {
                    "цена": int(entries["цена"].get()),
                    "объем": entries["объем"].get()
                }

            self.config_manager.save_menu_config(adult_menu, 'menu_adult.txt')

            # Сохранение меню детское
            minor_menu = {"Пиццы": {}, "Напитки": {}}
            for pizza, entries in self.menu_minor_entries["Пиццы"].items():
                minor_menu["Пиццы"][pizza] = {
                    "цена": int(entries["цена"].get()),
                    "размер": entries["размер"].get(),
                    "ингредиенты": entries["ингредиенты"].get()
                }

            for drink, entries in self.menu_minor_entries["Напитки"].items():
                minor_menu["Напитки"][drink] = {
                    "цена": int(entries["цена"].get()),
                    "объем": entries["объем"].get()
                }

            self.config_manager.save_menu_config(minor_menu, 'menu_minor.txt')

            # Сохранение начинок
            toppings_data = {}
            for topping, entry in self.topping_entries.items():
                toppings_data[topping] = int(entry.get())

            self.config_manager.save_toppings(toppings_data)

            # Сохранение скидок
            discounts_data = {"напитки": {}}
            for volume, entry in self.discount_entries.items():
                try:
                    discount = float(entry.get())
                    discounts_data["напитки"][volume] = discount
                except ValueError:
                    discounts_data["напитки"][volume] = 0.0

            self.config_manager.save_discounts(discounts_data)

            # Перезагрузка конфигурации в основном приложении
            self.parent.load_configuration()

            messagebox.showinfo("Успех", "Настройки сохранены!")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения настроек: {e}")


if __name__ == "__main__":
    # Проверка существования конфигурационных файлов
    if not os.path.exists('config'):
        messagebox.showwarning(
            "Внимание",
            "Конфигурационные файлы не найдены!\nЗапустите setup.py для установки."
        )
    else:
        app = PizzaMakerApp()
        app.mainloop()
