import customtkinter as ctk
import pandas as pd
import qrcode
import os
import configparser
from datetime import datetime
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
from tkinter import simpledialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ConfigManager:
    """Менеджер конфигурационных файлов"""

    @staticmethod
    def load_receipt_config():
        """Загрузка настроек чека"""
        config = configparser.ConfigParser()
        config.read('config/receipt_config.txt', encoding='utf-8')
        return config

    @staticmethod
    def load_menu_config(menu_file):
        """Загрузка меню из файла"""
        menu = {"Пиццы": {}, "Напитки": {}}
        config = configparser.ConfigParser()
        config.read(f'config/{menu_file}', encoding='utf-8')

        if 'Пиццы' in config:
            for pizza, value in config['Пиццы'].items():
                price, size, ingredients = value.split('|')
                menu["Пиццы"][pizza.replace('_', ' ')] = {
                    "цена": int(price),
                    "размер": size,
                    "ингредиенты": ingredients
                }

        if 'Напитки' in config:
            for drink, value in config['Напитки'].items():
                price, volume = value.split('|')
                menu["Напитки"][drink] = {"цена": int(price), "объем": volume}

        return menu

    @staticmethod
    def load_toppings():
        """Загрузка начинок"""
        toppings = {}
        with open('config/toppings.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    topping, price = line.strip().split('=')
                    toppings[topping] = int(price)
        return toppings

    @staticmethod
    def save_receipt_config(config_data):
        """Сохранение настроек чека"""
        config = configparser.ConfigParser()
        config['Чек'] = config_data['receipt']
        config['QR'] = config_data['qr']

        with open('config/receipt_config.txt', 'w', encoding='utf-8') as f:
            config.write(f)

    @staticmethod
    def save_menu_config(menu_data, menu_file):
        """Сохранение меню в файл"""
        config = configparser.ConfigParser()

        # Пиццы
        config['Пиццы'] = {}
        for pizza, info in menu_data["Пиццы"].items():
            config['Пиццы'][pizza.replace(
                ' ', '_'
            )] = f"{info['цена']}|{info['размер']}|{info['ингредиенты']}"

        # Напитки
        config['Напитки'] = {}
        for drink, info in menu_data["Напитки"].items():
            config['Напитки'][drink] = f"{info['цена']}|{info['объем']}"

        with open(f'config/{menu_file}', 'w', encoding='utf-8') as f:
            config.write(f)

    @staticmethod
    def save_toppings(toppings_data):
        """Сохранение начинок"""
        with open('config/toppings.txt', 'w', encoding='utf-8') as f:
            for topping, price in toppings_data.items():
                f.write(f"{topping}={price}\n")


class PizzaMakerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Pizza Maker 🍕")
        self.geometry("1000x700")
        self.resizable(True, True)

        self.orders_file = "orders.xlsx"
        self.inventory_file = "inventory.xlsx"
        self.config_manager = ConfigManager()

        # Загрузка конфигурации
        self.load_configuration()

        # Данные пользователя
        self.user_data = {}
        self.current_order = []
        self.total_amount = 0

        self.create_welcome_frame()

    def load_configuration(self):
        """Загрузка всей конфигурации"""
        try:
            self.receipt_config = self.config_manager.load_receipt_config()
            self.menu_adult = self.config_manager.load_menu_config(
                'menu_adult.txt')
            self.menu_minor = self.config_manager.load_menu_config(
                'menu_minor.txt')
            self.toppings = self.config_manager.load_toppings()
        except Exception as e:
            messagebox.showerror("Ошибка",
                                 f"Ошибка загрузки конфигурации: {e}")
            self.create_default_config()

    def create_default_config(self):
        """Создание конфигурации по умолчанию"""
        self.receipt_config = configparser.ConfigParser()
        self.receipt_config['Чек'] = {
            'Название_компании': 'Pizza Maker',
            'ИНН': '1234567890',
            'Адрес': 'г. Москва, ул. Пушкина, д. 1',
            'Телефон': '+7 (495) 123-45-67',
            'Сайт': 'https://pizza-maker.ru',
            'НДС': '20%'
        }
        self.receipt_config['QR'] = {
            'Ссылка': 'https://genius-school.kuzstu.ru/pizza-maker'
        }

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

        tab_pizzas = tabview.add("Пиццы")
        tab_drinks = tabview.add("Напитки")

        # Отображение пицц с выбором размера
        for pizza, info in menu["Пиццы"].items():
            pizza_frame = ctk.CTkFrame(tab_pizzas)
            pizza_frame.pack(pady=5, padx=10, fill="x")

            pizza_text = f"{pizza} - {info['цена']} руб. ({info['размер']})"
            ctk.CTkLabel(pizza_frame,
                         text=pizza_text,
                         font=ctk.CTkFont(size=14,
                                          weight="bold")).pack(anchor="w")

            ctk.CTkLabel(pizza_frame,
                         text=info['ингредиенты'],
                         font=ctk.CTkFont(size=12),
                         text_color="gray").pack(anchor="w")

            # Выбор размера
            size_frame = ctk.CTkFrame(pizza_frame)
            size_frame.pack(anchor="w", pady=5)

            ctk.CTkLabel(size_frame, text="Размер:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            size_var = ctk.StringVar(value=info['размер'])

            # Определяем размеры и цены
            base_price = info['цена']
            size_prices = {}
            if is_adult:
                size_prices = {
                    "Маленькая": int(base_price * 0.7),
                    "Средняя": int(base_price * 0.85),
                    "Большая": base_price
                }
            else:
                size_prices = {
                    "Маленькая": int(base_price * 0.75),
                    "Средняя": base_price,
                    "Большая": int(base_price * 1.2)
                }

            size_options = list(size_prices.keys())
            size_menu = ctk.CTkOptionMenu(size_frame, variable=size_var, values=size_options, width=120)
            size_menu.pack(side="left", padx=5)

            add_btn = ctk.CTkButton(pizza_frame,
                                    text="Добавить",
                                    command=lambda p=pizza, sz=size_var, sp=size_prices:
                                    self.add_pizza_with_size(p, sz, sp),
                                    width=100)
            add_btn.pack(anchor="e", pady=5)

            if pizza == "Кастомная":
                custom_btn = ctk.CTkButton(
                    pizza_frame,
                    text="Создать свою",
                    command=self.create_custom_pizza_dialog,
                    width=100,
                    fg_color="green",
                    hover_color="#006400")
                custom_btn.pack(anchor="e", pady=5)

        # Отображение напитков с выбором объема
        for drink, info in menu["Напитки"].items():
            drink_frame = ctk.CTkFrame(tab_drinks)
            drink_frame.pack(pady=5, padx=10, fill="x")

            drink_text = f"{drink} - {info['цена']} руб. ({info['объем']})"
            ctk.CTkLabel(drink_frame,
                         text=drink_text,
                         font=ctk.CTkFont(size=14,
                                          weight="bold")).pack(anchor="w")

            # Выбор объема
            volume_frame = ctk.CTkFrame(drink_frame)
            volume_frame.pack(anchor="w", pady=5)

            ctk.CTkLabel(volume_frame, text="Объем:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            volume_var = ctk.StringVar(value=info['объем'])
            volume_options = ["0.33л", "0.5л", "1л", "1.5л", "2л"]
            volume_menu = ctk.CTkOptionMenu(volume_frame, variable=volume_var, values=volume_options, width=100)
            volume_menu.pack(side="left", padx=5)

            add_btn = ctk.CTkButton(drink_frame,
                                    text="Добавить",
                                    command=lambda d=drink, price=info['цена'], vol=volume_var:
                                    self.add_drink_with_volume(d, price, vol),
                                    width=100)
            add_btn.pack(anchor="e", pady=5)

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

    def add_pizza_with_size(self, pizza, size_var, size_prices):
        """Добавление пиццы с выбранным размером"""
        size = size_var.get()
        price = size_prices[size]
        item_name = f"{pizza} ({size})"
        self.current_order.append({"item": item_name, "price": price, "quantity": 1})
        self.total_amount += price
        self.update_cart_display()
        messagebox.showinfo("Успех", f"{item_name} добавлена в корзину!")

    def add_drink_with_volume(self, drink, price, volume_var):
        """Добавление напитка с выбранным объемом"""
        volume = volume_var.get()
        item_name = f"{drink} ({volume})"
        self.current_order.append({"item": item_name, "price": price, "quantity": 1})
        self.total_amount += price
        self.update_cart_display()
        messagebox.showinfo("Успех", f"{item_name} добавлен в корзину!")

    def add_to_cart(self, item, price):
        self.current_order.append({"item": item, "price": price, "quantity": 1})
        self.total_amount += price
        self.update_cart_display()
        messagebox.showinfo("Успех", f"{item} добавлен в корзину!")

    def update_cart_display(self):
        self.cart_textbox.delete("1.0", "end")
        if not self.current_order:
            self.cart_textbox.insert("1.0", "Корзина пуста")
            return

        for i, order_item in enumerate(self.current_order, 1):
            self.cart_textbox.insert(
                "end",
                f"{i}. {order_item['item']} - {order_item['price']} руб.\n")

    def clear_cart(self):
        self.current_order = []
        self.total_amount = 0
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
        order_items = [item["item"] for item in self.current_order]

        # Сохранение в Excel
        try:
            df = pd.read_excel(self.orders_file)
            new_order = {
                "ID": receipt_id,
                "Дата": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                "ФИО": self.user_data["fio"],
                "Возраст": self.user_data["age"],
                "Заказ": "; ".join(order_items),
                "Сумма": self.total_amount,
                "Оплата": payment_method,
                "Сдача": change
            }
            df = pd.concat([df, pd.DataFrame([new_order])], ignore_index=True)
            df.to_excel(self.orders_file, index=False)
        except Exception as e:
            print(f"Ошибка при сохранении заказа: {e}")

        # Генерация QR-кода
        self.generate_qr_code(receipt_id)

        # Обновление остатков
        self.update_inventory(order_items)

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
            img.save(f"receipt_{receipt_id}.png")

        except Exception as e:
            print(f"Ошибка при генерации QR-кода: {e}")

    def generate_pdf_receipt(self, receipt_id, payment_method, change):
        """Генерация чека в формате PDF по ФЗ-54"""
        try:
            pdf_filename = f"receipt_{receipt_id}.pdf"
            c = canvas.Canvas(pdf_filename, pagesize=letter)
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

            # ТОВАРЫ (с количеством, ценой, суммой)
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
                # Количество x Цена = Сумма
                c.drawString(110, y_position, f"{quantity} x {price}.00 = {total}.00")
                y_position -= 12
                # НДС 20%
                c.drawString(110, y_position, f"НДС 20%: {item_vat}.00")
                y_position -= 18

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
            qr_image_path = f"receipt_{receipt_id}.png"
            if os.path.exists(qr_image_path):
                c.drawImage(qr_image_path, 180, 50, width=150, height=150)

            c.save()
            return pdf_filename

        except Exception as e:
            print(f"Ошибка при генерации PDF: {e}")
            return None

    def update_inventory(self, order_items):
        try:
            df = pd.read_excel(self.inventory_file)

            for item in order_items:
                if "пицца" in item.lower():
                    df.loc[df["Продукт"] == "Тесто", "Количество"] -= 1
                    df.loc[df["Продукт"] == "Сыр", "Количество"] -= 0.2

                for topping in self.toppings.keys():
                    if topping.lower() in item.lower():
                        df.loc[df["Продукт"] == topping, "Количество"] -= 0.05

                for drink in ["Кола", "Фанта", "Спрайт", "Вода", "Сок"]:
                    if drink in item:
                        df.loc[df["Продукт"] == drink, "Количество"] -= 1

            df.to_excel(self.inventory_file, index=False)
        except Exception as e:
            print(f"Ошибка при обновлении остатков: {e}")

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

        receipt_text += f"\nИТОГО: {self.total_amount} руб."
        receipt_text += f"\nНДС: {vat}"
        receipt_text += f"\nОплата: {payment_method}"

        if payment_method == "Наличные":
            receipt_text += f"\nВнесено: {self.total_amount + change} руб."
            receipt_text += f"\nСдача: {change} руб."

        receipt_text += f"\n\nPDF чек сохранен: {pdf_file}"

        receipt_display = ctk.CTkTextbox(receipt_frame,
                                         font=ctk.CTkFont(family="Courier",
                                                          size=12))
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
                      text="💾 Скачать",
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
            messagebox.showinfo("Успех", f"Чек сохранен: {pdf_file}")
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
        self.load_configuration()  # Перезагрузка конфигурации
        self.create_welcome_frame()


class SettingsWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config_manager = parent.config_manager

        self.title("Настройки Pizza Maker")
        self.geometry("800x600")
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

        self.create_receipt_tab(tab_receipt)
        self.create_menu_tab(tab_menu_adult, "adult")
        self.create_menu_tab(tab_menu_minor, "minor")
        self.create_toppings_tab(tab_toppings)

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
                     font=ctk.CTkFont(size=16,
                                      weight="bold")).pack(anchor="w",
                                                           pady=(10, 5))

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

            ctk.CTkLabel(entry_frame, text="Ингредиенты:").pack(side="left",
                                                                padx=5)
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
                     font=ctk.CTkFont(size=16,
                                      weight="bold")).pack(anchor="w",
                                                           pady=(20, 5))

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

            ctk.CTkLabel(frame, text=topping, width=150).pack(side="left",
                                                              padx=10)
            price_entry = ctk.CTkEntry(frame, width=100)
            price_entry.insert(0, str(price))
            price_entry.pack(side="left", padx=10)

            self.topping_entries[topping] = price_entry

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
