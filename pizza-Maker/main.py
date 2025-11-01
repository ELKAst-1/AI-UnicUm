import streamlit as st
import pandas as pd
import qrcode
import os
import configparser
from datetime import datetime
from PIL import Image
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')

st.set_page_config(
    page_title="Pizza Maker 🍕",
    page_icon="🍕",
    layout="wide"
)


class ConfigManager:
    @staticmethod
    def load_receipt_config():
        config = configparser.ConfigParser()
        config.read('config/receipt_config.txt', encoding='utf-8')
        return config

    @staticmethod
    def load_menu_config(menu_file):
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
        toppings = {}
        with open('config/toppings.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    topping, price = line.strip().split('=')
                    toppings[topping] = int(price)
        return toppings

    @staticmethod
    def load_discounts():
        discounts = {}
        config = configparser.ConfigParser()
        config.read('config/discounts.txt', encoding='utf-8')

        for section in config.sections():
            discounts[section] = {
                'название': config[section].get('Название', ''),
                'процент': int(config[section].get('Процент', '0')),
                'условие': config[section].get('Условие', ''),
                'активна': config[section].getboolean('Активна', False)
            }
        return discounts

    @staticmethod
    def save_discounts(discounts):
        config = configparser.ConfigParser()
        for key, value in discounts.items():
            config[key] = {
                'Название': value['название'],
                'Процент': str(value['процент']),
                'Условие': value['условие'],
                'Активна': str(value['активна'])
            }

        with open('config/discounts.txt', 'w', encoding='utf-8') as f:
            config.write(f)


class PriceCalculator:
    @staticmethod
    def calculate_price_with_discount(base_price, size, discounts):
        price = base_price
        discount_applied = 0

        for discount_data in discounts.values():
            if discount_data['активна'] and discount_data['условие'] in size:
                discount_percent = discount_data['процент']
                discount_amount = int(price * discount_percent / 100)
                price -= discount_amount
                discount_applied += discount_percent

        return price, discount_applied


def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def generate_receipt_pdf(order_data, receipt_config, qr_image_path):
    receipt_path = f"receipts/receipt_{order_data['ID']}.pdf"
    c = canvas.Canvas(receipt_path, pagesize=letter)
    width, height = letter

    y_position = height - 50

    c.setFont("Helvetica-Bold", 16)
    company_name = receipt_config['Чек'].get('Название_компании', 'Pizza Maker')
    c.drawString(50, y_position, company_name)
    y_position -= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, f"ИНН: {receipt_config['Чек'].get('ИНН', '')}")
    y_position -= 15
    c.drawString(50, y_position, f"Адрес: {receipt_config['Чек'].get('Адрес', '')}")
    y_position -= 15
    c.drawString(50, y_position, f"Телефон: {receipt_config['Чек'].get('Телефон', '')}")
    y_position -= 15
    c.drawString(50, y_position, f"Сайт: {receipt_config['Чек'].get('Сайт', '')}")
    y_position -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, f"ЧЕК #{order_data['ID']}")
    y_position -= 15
    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, f"Дата: {order_data['Дата']}")
    y_position -= 15
    c.drawString(50, y_position, f"Клиент: {order_data['ФИО']}")
    y_position -= 30

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y_position, "ЗАКАЗ:")
    y_position -= 20

    c.setFont("Helvetica", 10)
    for item in order_data['Заказ'].split('\n'):
        if item.strip():
            c.drawString(70, y_position, item)
            y_position -= 15

    y_position -= 10

    if order_data.get('Комментарий') and order_data['Комментарий'].strip():
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y_position, "Комментарий к заказу:")
        y_position -= 15
        c.setFont("Helvetica", 10)
        c.drawString(70, y_position, order_data['Комментарий'])
        y_position -= 20

    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, f"Сумма: {order_data['Сумма']} руб.")
    y_position -= 15

    if order_data.get('Скидка', 0) > 0:
        c.drawString(50, y_position, f"Скидка: {order_data['Скидка']}%")
        y_position -= 15

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, f"ИТОГО: {order_data['Итого']} руб.")
    y_position -= 15

    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, f"Оплата: {order_data['Оплата']}")
    y_position -= 15

    if order_data.get('Сдача', 0) > 0:
        c.drawString(50, y_position, f"Сдача: {order_data['Сдача']} руб.")
        y_position -= 15

    y_position -= 20
    c.drawString(50, y_position, f"НДС: {receipt_config['Чек'].get('НДС', '20%')}")
    y_position -= 40

    if os.path.exists(qr_image_path):
        c.drawImage(qr_image_path, 50, y_position - 100, width=100, height=100)

    c.save()
    return receipt_path


def save_order_to_excel(order_data):
    df = pd.read_excel('orders.xlsx')
    new_row = pd.DataFrame([order_data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel('orders.xlsx', index=False)


def show_analytics():
    st.title("📊 Аналитика и Настройки Администратора")

    tab1, tab2 = st.tabs(["📈 Аналитика", "⚙️ Настройки Скидок"])

    with tab1:
        st.subheader("Анализ заказов")

        try:
            df = pd.read_excel('orders.xlsx')

            if len(df) == 0:
                st.info("Пока нет данных для аналитики. Оформите первый заказ!")
                return

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🍕 Популярные заказы")

                all_items = []
                for order in df['Заказ']:
                    items = str(order).split('\n')
                    for item in items:
                        if item.strip() and '-' in item:
                            item_name = item.split('-')[0].strip()
                            item_name = item_name.split('•')[-1].strip()
                            all_items.append(item_name)

                if all_items:
                    item_counts = pd.Series(all_items).value_counts().head(10)

                    fig, ax = plt.subplots(figsize=(10, 6))
                    colors = plt.cm.Set3(range(len(item_counts)))
                    bars = ax.bar(range(len(item_counts)), item_counts.values, color=colors)
                    ax.set_xlabel('Товары', fontsize=12)
                    ax.set_ylabel('Количество заказов', fontsize=12)
                    ax.set_title('Топ-10 самых популярных товаров', fontsize=14, fontweight='bold')
                    ax.set_xticks(range(len(item_counts)))
                    ax.set_xticklabels(item_counts.index, rotation=45, ha='right')
                    ax.grid(axis='y', alpha=0.3)

                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2., height,
                                f'{int(height)}',
                                ha='center', va='bottom', fontsize=10)

                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()

                    st.markdown("#### 📋 Статистика:")
                    st.write(f"- Всего уникальных товаров: {len(item_counts)}")
                    st.write(f"- Самый популярный: {item_counts.index[0]} ({item_counts.values[0]} заказов)")
                else:
                    st.warning("Нет данных о товарах")

            with col2:
                st.markdown("### 👥 Распределение возраста клиентов")

                age_bins = [0, 12, 17, 25, 35, 50, 100]
                age_labels = ['0-12', '13-17', '18-25', '26-35', '36-50', '50+']
                df['Возрастная группа'] = pd.cut(df['Возраст'], bins=age_bins, labels=age_labels)

                age_counts = df['Возрастная группа'].value_counts().sort_index()

                fig, ax = plt.subplots(figsize=(10, 6))
                colors = plt.cm.Pastel1(range(len(age_counts)))
                bars = ax.bar(range(len(age_counts)), age_counts.values, color=colors)
                ax.set_xlabel('Возрастные группы', fontsize=12)
                ax.set_ylabel('Количество клиентов', fontsize=12)
                ax.set_title('Распределение клиентов по возрасту', fontsize=14, fontweight='bold')
                ax.set_xticks(range(len(age_counts)))
                ax.set_xticklabels(age_counts.index, rotation=0)
                ax.grid(axis='y', alpha=0.3)

                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontsize=10)

                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

                st.markdown("#### 📋 Статистика:")
                st.write(f"- Средний возраст: {df['Возраст'].mean():.1f} лет")
                st.write(f"- Минимальный возраст: {df['Возраст'].min()} лет")
                st.write(f"- Максимальный возраст: {df['Возраст'].max()} лет")

            st.markdown("---")
            st.markdown("### 💰 Общая статистика продаж")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Всего заказов", len(df))
            with col2:
                st.metric("Общая выручка", f"{df['Итого'].sum():.0f} ₽")
            with col3:
                st.metric("Средний чек", f"{df['Итого'].mean():.0f} ₽")
            with col4:
                total_discount = df[df['Скидка'] > 0]['Скидка'].count()
                st.metric("Применено скидок", total_discount)

        except Exception as e:
            st.error(f"Ошибка загрузки данных: {e}")

    with tab2:
        st.subheader("Управление скидками")

        discounts = ConfigManager.load_discounts()

        st.markdown("### Скидка 1")
        col1, col2 = st.columns(2)
        with col1:
            discount1_name = st.text_input("Название скидки 1",
                                           value=discounts.get('Скидка1', {}).get('название', ''))
            discount1_percent = st.slider("Процент скидки 1", 0, 50,
                                          discounts.get('Скидка1', {}).get('процент', 0))
        with col2:
            discount1_condition = st.selectbox("Условие применения 1",
                                               ["Маленькая", "Средняя", "Большая"],
                                               index=["Маленькая", "Средняя", "Большая"].index(
                                                   discounts.get('Скидка1', {}).get('условие', 'Большая')))
            discount1_active = st.checkbox("Активна скидка 1",
                                           value=discounts.get('Скидка1', {}).get('активна', False))

        st.markdown("---")
        st.markdown("### Скидка 2")
        col1, col2 = st.columns(2)
        with col1:
            discount2_name = st.text_input("Название скидки 2",
                                           value=discounts.get('Скидка2', {}).get('название', ''))
            discount2_percent = st.slider("Процент скидки 2", 0, 50,
                                          discounts.get('Скидка2', {}).get('процент', 0))
        with col2:
            discount2_condition = st.selectbox("Условие применения 2",
                                               ["Маленькая", "Средняя", "Большая"],
                                               index=["Маленькая", "Средняя", "Большая"].index(
                                                   discounts.get('Скидка2', {}).get('условие', 'Маленькая')))
            discount2_active = st.checkbox("Активна скидка 2",
                                           value=discounts.get('Скидка2', {}).get('активна', False))

        st.markdown("---")

        if st.button("💾 Сохранить настройки скидок", type="primary"):
            new_discounts = {
                'Скидка1': {
                    'название': discount1_name,
                    'процент': discount1_percent,
                    'условие': discount1_condition,
                    'активна': discount1_active
                },
                'Скидка2': {
                    'название': discount2_name,
                    'процент': discount2_percent,
                    'условие': discount2_condition,
                    'активна': discount2_active
                }
            }
            ConfigManager.save_discounts(new_discounts)
            st.success("✅ Настройки скидок сохранены!")
            st.rerun()


def show_main_page():
    st.title("🍕 Pizza Maker")
    st.markdown("### Добро пожаловать в систему заказа пиццы!")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Введите ваши данные")

        fio = st.text_input("ФИО", placeholder="Введите ваше ФИО")
        age = st.number_input("Возраст", min_value=1, max_value=120, value=25)

        st.markdown("#### Комментарий к заказу (необязательно)")
        comment = st.text_area("Ваш комментарий",
                               placeholder="Например: без лука, доставка к 18:00 и т.д.",
                               height=100)

        if st.button("▶️ Продолжить к меню", type="primary"):
            if not fio:
                st.error("Пожалуйста, введите ФИО")
            else:
                st.session_state['user_data'] = {
                    'fio': fio,
                    'age': age,
                    'comment': comment
                }
                st.session_state['page'] = 'menu'
                st.rerun()

    with col2:
        st.info("""
        **Как заказать:**

        1. Введите ФИО и возраст
        2. Добавьте комментарий (по желанию)
        3. Выберите пиццу и напитки
        4. Оформите заказ
        5. Получите чек с QR-кодом

        **Скидки применяются автоматически!**
        """)


def show_menu_page():
    if 'user_data' not in st.session_state:
        st.session_state['page'] = 'main'
        st.rerun()
        return

    user_data = st.session_state['user_data']
    is_adult = user_data['age'] >= 18

    st.title(f"🍕 Меню для {user_data['fio']}")

    if is_adult:
        st.success("✨ Вам доступно взрослое меню с расширенным выбором!")
        menu = ConfigManager.load_menu_config('menu_adult.txt')
    else:
        st.info("🎈 Детское меню специально для вас!")
        menu = ConfigManager.load_menu_config('menu_minor.txt')

    discounts = ConfigManager.load_discounts()

    active_discounts = [d for d in discounts.values() if d['активна']]
    if active_discounts:
        st.markdown("### 🎉 Активные скидки:")
        cols = st.columns(len(active_discounts))
        for i, discount in enumerate(active_discounts):
            with cols[i]:
                st.success(f"**{discount['название']}**: {discount['процент']}% на {discount['условие']}")

    if 'cart' not in st.session_state:
        st.session_state['cart'] = []

    col1, col2 = st.columns([2, 1])

    with col1:
        tab1, tab2 = st.tabs(["🍕 Пиццы", "🥤 Напитки"])

        with tab1:
            st.markdown("### Выберите пиццу")

            for pizza_name, pizza_info in menu["Пиццы"].items():
                with st.expander(f"🍕 {pizza_name}", expanded=False):
                    st.write(f"**Ингредиенты:** {pizza_info['ингредиенты']}")

                    size = st.selectbox(
                        "Размер",
                        ["Маленькая", "Средняя", "Большая"],
                        key=f"size_{pizza_name}"
                    )

                    base_price = pizza_info['цена']

                    if is_adult:
                        size_multipliers = {"Маленькая": 0.7, "Средняя": 0.85, "Большая": 1.0}
                    else:
                        size_multipliers = {"Маленькая": 0.75, "Средняя": 1.0, "Большая": 1.2}

                    price_before_discount = int(base_price * size_multipliers[size])
                    final_price, discount_percent = PriceCalculator.calculate_price_with_discount(
                        price_before_discount, size, discounts
                    )

                    if discount_percent > 0:
                        st.markdown(f"~~{price_before_discount} ₽~~ → **{final_price} ₽** (скидка {discount_percent}%)")
                    else:
                        st.markdown(f"**Цена: {final_price} ₽**")

                    if st.button(f"➕ Добавить {pizza_name}", key=f"add_{pizza_name}"):
                        st.session_state['cart'].append({
                            'name': f"{pizza_name} ({size})",
                            'price': final_price,
                            'discount': discount_percent
                        })
                        st.success(f"✅ {pizza_name} ({size}) добавлена в корзину!")
                        st.rerun()

        with tab2:
            st.markdown("### Выберите напиток")

            for drink_name, drink_info in menu["Напитки"].items():
                with st.expander(f"🥤 {drink_name}", expanded=False):
                    volume = st.selectbox(
                        "Объем",
                        ["0.33л", "0.5л", "1л", "1.5л", "2л"],
                        key=f"volume_{drink_name}"
                    )

                    base_price = drink_info['цена']
                    volume_multipliers = {
                        "0.33л": 0.6,
                        "0.5л": 0.75,
                        "1л": 1.0,
                        "1.5л": 1.4,
                        "2л": 1.8
                    }

                    price_before_discount = int(base_price * volume_multipliers[volume])
                    final_price, discount_percent = PriceCalculator.calculate_price_with_discount(
                        price_before_discount, volume, discounts
                    )

                    if discount_percent > 0:
                        st.markdown(f"~~{price_before_discount} ₽~~ → **{final_price} ₽** (скидка {discount_percent}%)")
                    else:
                        st.markdown(f"**Цена: {final_price} ₽**")

                    if st.button(f"➕ Добавить {drink_name}", key=f"add_{drink_name}"):
                        st.session_state['cart'].append({
                            'name': f"{drink_name} ({volume})",
                            'price': final_price,
                            'discount': discount_percent
                        })
                        st.success(f"✅ {drink_name} ({volume}) добавлен в корзину!")
                        st.rerun()

    with col2:
        st.markdown("### 🛒 Ваша корзина")

        if st.session_state['cart']:
            total = 0
            max_discount = 0

            for i, item in enumerate(st.session_state['cart']):
                st.write(f"{i + 1}. {item['name']} - {item['price']} ₽")
                total += item['price']
                if item['discount'] > max_discount:
                    max_discount = item['discount']

            st.markdown("---")
            st.markdown(f"**Итого: {total} ₽**")

            if max_discount > 0:
                st.success(f"Применена скидка: {max_discount}%")

            payment_method = st.radio("Способ оплаты", ["Карта", "Наличные"])

            cash_amount = 0
            if payment_method == "Наличные":
                cash_amount = st.number_input("Сумма наличных", min_value=total, value=total)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Оформить заказ", type="primary"):
                    order_id = datetime.now().strftime("%Y%m%d%H%M%S")

                    order_items = '\n'.join([f"• {item['name']} - {item['price']} руб."
                                             for item in st.session_state['cart']])

                    change = cash_amount - total if payment_method == "Наличные" else 0

                    qr_data = f"Заказ #{order_id}\nКлиент: {user_data['fio']}\nСумма: {total} руб."
                    if user_data['comment']:
                        qr_data += f"\nКомментарий: {user_data['comment']}"

                    qr_image = generate_qr_code(qr_data)
                    qr_path = f"receipts/qr_{order_id}.png"

                    os.makedirs('receipts', exist_ok=True)
                    with open(qr_path, 'wb') as f:
                        f.write(qr_image.getvalue())

                    order_data = {
                        'ID': order_id,
                        'Дата': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'ФИО': user_data['fio'],
                        'Возраст': user_data['age'],
                        'Заказ': order_items,
                        'Комментарий': user_data['comment'],
                        'Сумма': total,
                        'Скидка': max_discount,
                        'Итого': total,
                        'Оплата': payment_method,
                        'Сдача': change
                    }

                    receipt_config = ConfigManager.load_receipt_config()
                    receipt_path = generate_receipt_pdf(order_data, receipt_config, qr_path)

                    save_order_to_excel(order_data)

                    st.success(f"✅ Заказ #{order_id} оформлен!")

                    with open(receipt_path, 'rb') as f:
                        st.download_button(
                            "📥 Скачать чек",
                            f,
                            file_name=f"receipt_{order_id}.pdf",
                            mime="application/pdf"
                        )

                    st.session_state['cart'] = []
                    st.balloons()

            with col_b:
                if st.button("🗑️ Очистить"):
                    st.session_state['cart'] = []
                    st.rerun()
        else:
            st.info("Корзина пуста")

        if st.button("⬅️ Назад"):
            st.session_state['page'] = 'main'
            st.rerun()


def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'

    st.sidebar.title("🍕 Навигация")
    page = st.sidebar.radio(
        "Выберите страницу:",
        ["🏠 Главная", "📊 Админ-панель"],
        index=0 if st.session_state['page'] == 'main' else 1
    )

    if page == "🏠 Главная":
        if st.session_state['page'] == 'menu':
            show_menu_page()
        else:
            show_main_page()
    else:
        show_analytics()


if __name__ == "__main__":
    main()
