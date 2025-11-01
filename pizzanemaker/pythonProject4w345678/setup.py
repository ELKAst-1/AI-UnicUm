import os
import subprocess
import sys
import shutil


def install_requirements():
    """Установка необходимых библиотек"""
    requirements = [
        'customtkinter==5.2.2', 'pandas>=2.0.0', 'openpyxl==3.0.10',
        'qrcode[pil]==7.3.1', 'Pillow==9.4.0', 'numpy<2.0.0'
    ]

    print("Установка необходимых библиотек...")
    for package in requirements:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package])
            print(f"✓ Установлено: {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Ошибка установки: {package}")


def create_config_files():
    """Создание конфигурационных файлов"""
    config_files = {
        'config/receipt_config.txt':
        """[Чек]
Название_компании=Pizza Maker
ИНН=1234567890
Адрес=г. Москва, ул. Пушкина, д. 1
Телефон=+7 (495) 123-45-67
Сайт=https://pizza-maker.ru
НДС=20%%

[QR]
Ссылка=https://genius-school.kuzstu.ru/pizza-maker
""",
        'config/menu_adult.txt':
        """[Пиццы]
Маргарита=450|Большая|сыр, томаты, соус
Пепперони=550|Большая|пепперони, сыр, соус
Гавайская=500|Большая|ветчина, ананасы, сыр
Четыре_сыра=600|Большая|4 вида сыра
Кастомная=400|Большая|на ваш выбор

[Напитки]
Кола=150|1л
Фанта=150|1л
Спрайт=150|1л
Вода=100|1л
Сок=200|1л
""",
        'config/menu_minor.txt':
        """[Пиццы]
Маргарита=350|Средняя|сыр, томаты, соус
Пепперони=450|Средняя|пепперони, сыр, соус
Гавайская=400|Средняя|ветчина, ананасы, сыр
Четыре_сыра=500|Средняя|4 вида сыра
Кастомная=300|Средняя|на ваш выбор

[Напитки]
Кола=100|0.5л
Фанта=100|0.5л
Спрайт=100|0.5л
Вода=80|0.5л
Сок=150|0.5л
""",
        'config/toppings.txt':
        """Сыр=50
Пепперони=70
Ветчина=60
Грибы=40
Ананасы=45
Оливки=35
Томаты=30
Лук=25
Перец=35
"""
    }

    print("Создание конфигурационных файлов...")
    if not os.path.exists('config'):
        os.makedirs('config')

    for file_path, content in config_files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Создан: {file_path}")


def create_data_files():
    """Создание файлов данных"""
    import pandas as pd

    print("Создание файлов данных...")

    # Файл заказов
    orders_data = pd.DataFrame(columns=[
        "ID", "Дата", "ФИО", "Возраст", "Заказ", "Сумма", "Оплата", "Сдача"
    ])
    orders_data.to_excel('orders.xlsx', index=False)
    print("✓ Создан: orders.xlsx")

    # Файл остатков
    inventory_data = {
        "Продукт": [
            "Тесто", "Сыр", "Пепперони", "Ветчина", "Грибы", "Ананасы",
            "Оливки", "Томаты", "Лук", "Перец", "Кола", "Фанта", "Спрайт",
            "Вода", "Сок"
        ],
        "Количество":
        [100, 100, 50, 40, 30, 25, 20, 35, 25, 30, 50, 50, 50, 50, 40],
        "Единица": [
            "шт", "кг", "кг", "кг", "кг", "кг", "кг", "кг", "кг", "кг", "л",
            "л", "л", "л", "л"
        ]
    }
    inventory_df = pd.DataFrame(inventory_data)
    inventory_df.to_excel('inventory.xlsx', index=False)
    print("✓ Создан: inventory.xlsx")


def main():
    print("=" * 50)
    print("       УСТАНОВЩИК PIZZA MAKER")
    print("=" * 50)

    try:
        install_requirements()
        create_config_files()
        create_data_files()

        print("\n" + "=" * 50)
        print("Установка завершена успешно! 🎉")
        print("Запустите приложение: python pizza_maker_app.py")
        print("=" * 50)

    except Exception as e:
        print(f"\nОшибка установки: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
