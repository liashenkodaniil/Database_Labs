# Логіка роботи та взаємодії із базою даних
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, String, TIMESTAMP
from datetime import datetime
from faker import Faker
import random
import re


# - Для генерації псевдозначень
fake = Faker()

# - Створення генератора для трансляції python-команд в SQL команди
engine = create_engine('postgresql://postgres:11111@localhost/postgres')


# - Створення батьківського класу ORM
class Base(DeclarativeBase):
    pass


# - Створення session об'єкту, котрий дозволить нам звератися до БД
Session = sessionmaker(bind = engine)
session = Session()


# - Створення класів-сутностей до відповідних об'єктів-сутностей, представлених у відповідних таблицях БД
# - Клас користувачів
class Users(Base):
    __tablename__ = 'Users'
    user_id = Column(Integer, primary_key = True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    data_registration = Column(TIMESTAMP(timezone = True))
    email = Column(String(50))


# - Клас відгуків
class Review(Base):
    __tablename__ = 'Review'
    review_id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    realty_id = Column(Integer, ForeignKey('Realty.realty_id'))
    rating = Column(Integer)


# - Клас нерухомостей
class Realty(Base):
    __tablename__ = 'Realty'
    realty_id = Column(Integer, primary_key = True)
    property_owner_id = Column(Integer, ForeignKey('Property owner.property_owner_id'))
    city_name = Column(String(50))
    street_name = Column(String(50))
    type_realty = Column(String(50))
    status_realty = Column(String(50))
    minimum_rental_period = Column(Integer)
    deposit = Column(Integer)
    permitted_conditions = Column(String(50))
    price = Column(Integer)
    payment_term = Column(String(50))


# - Клас власників нерухомостей
class Property_owner(Base):
    __tablename__ = 'Property owner'
    property_owner_id = Column(Integer, primary_key = True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    data_registration = Column(TIMESTAMP(timezone = True))
    email = Column(String(50))


# - Клас бронювань
class Booking(Base):
    __tablename__ = 'Booking'
    booking_id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    realty_id = Column(Integer, ForeignKey('Realty.realty_id'))
    property_owner_id = Column(Integer, ForeignKey('Property owner.property_owner_id'))
    data_start = Column(TIMESTAMP(timezone = True))
    data_end = Column(TIMESTAMP(timezone = True))
    status_booking = Column(String(50))
    price_booking = Column(Integer)


# - Створення таблиць
Base.metadata.create_all(engine)


# - Клас об'єкта бізнес-логіки "Модель"
class Model:
    def __init__(self):
        self.gotten_data = []
        self.need_columns = []
        self.models = {
            "Users": Users,
            "Review": Review,
            "Realty": Realty,
            "Property owner": Property_owner,  
            "Booking": Booking
        }

    def get_table_schema_info(self, table_name: str) -> list:
        model_class = self.models.get(table_name)
        if not model_class:
            raise ValueError(f"Модель {table_name} не знайдена у self.models")
        columns_info = []
        for column in model_class.__mapper__.columns:
            try:
                python_type = column.type.python_type
            except NotImplementedError:
                python_type = str
            columns_info.append((column.name, python_type))
        return columns_info

    def get_tables_info(self) -> list:
        table_names = ["Users", "Review", "Realty", "Property owner", "Booking"]
        return [self.get_table_schema_info(name) for name in table_names]

    def generate_data(self, number_of_rows_str: str):
        try:
            num = int(number_of_rows_str)
            if num <= 0:
                print("\n# -> Кількість рядків повинна бути додатним числом.")
                input("Натисніть Enter для продовження...")
                return
        except (ValueError, TypeError):
            print("\n# -> ПОМИЛКА: Введіть коректне число.")
            input("Натисніть Enter для продовження...")
            return

        print(f"Генеруємо {num} наборів даних...")

        for _ in range(num):
            try:
                user_id = random.randint(10000000, 99999999)
                property_owner_id = random.randint(10000000, 99999999)
                realty_id = random.randint(10000000, 99999999)

                new_user = Users(
                    user_id=user_id,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    data_registration=fake.date_time(),
                    email=fake.email()
                )

                new_owner = Property_owner(
                    property_owner_id=property_owner_id,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    data_registration=fake.date_time(),
                    email=fake.email()
                )

                session.add(new_user)
                session.add(new_owner)
                session.commit()

                new_realty = Realty(
                    realty_id=realty_id,
                    property_owner_id=property_owner_id,
                    city_name=fake.city(),
                    street_name=fake.street_name(),
                    type_realty=random.choice(["Будинок", "Квартира"]),
                    status_realty=random.choice(["Здається в оренду", "Не здається в оренду", "Орендується"]),
                    minimum_rental_period=random.randint(1, 10),
                    deposit=random.randint(0, 10000),
                    permitted_conditions=random.choice(["Куріння заборонено", "Домашні тварини заборонені", "Домашні тварини дозволені"]),
                    price=random.randint(10000, 100000),
                    payment_term=random.choice(["Доба", "Місяць", "Рік"])
                )

                session.add(new_realty)
                session.commit()

                new_review = Review(
                    review_id=random.randint(10000000, 99999999),
                    user_id=user_id,
                    realty_id=realty_id,
                    rating=random.randint(1, 5)
                )

                new_booking = Booking(
                    booking_id=random.randint(10000000, 99999999),
                    user_id=user_id,
                    realty_id=realty_id,
                    property_owner_id=property_owner_id,
                    data_start=fake.date_time(),
                    data_end=fake.date_time(),
                    status_booking=random.choice(["Очікує підтвердження", "Підтверджено", "Відхилено", "Завершено"]),
                    price_booking=random.randint(10000, 100000)
                )

                session.add(new_review)
                session.add(new_booking)
                session.commit()

            except IntegrityError:
                session.rollback()
                print("---! Помилка генерації (дублікат ID), пропускаємо ітерацію.")
            except Exception as e:
                session.rollback()
                print(f"---! Критична помилка: {e}")

        print("Генерацію завершено.")
        

    def add_table_data(self, name_table: str, values: list):
        model_class = self.models.get(name_table)
        if not model_class:
            print(f"---!ERROR: Модель з іменем '{name_table}' не знайдена.")
            input("Натисніть Enter для продовження...")
            return
        try:
            table_schema = self.get_table_schema_info(table_name=name_table)
        except Exception as e:
            print(f"---!ERROR: Не вдалося отримати схему для {name_table}: {e}")
            input("Натисніть Enter для продовження...")
            return
        if len(table_schema) != len(values):
            print(f"---!ERROR: Кількість колонок ({len(table_schema)}) не збігається з кількістю значень ({len(values)}).")
            print(f"Очікувалось: {[col[0] for col in table_schema]}")
            print(f"Отримано:   {values}")
            input("Натисніть Enter для продовження...")
            return
        data_dict = {}
        try:
            for (col_name, expected_type), value in zip(table_schema, values):
                if expected_type == datetime:
                    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})([+-]\d{2})$', value)
                    if match:
                        value = match.group(1) + match.group(2) + ':00'
                    formats = [
                        '%Y-%m-%d %H:%M:%S%z',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d'
                    ]
                    parsed_value = None
                    for fmt in formats:
                        try:
                            parsed_value = datetime.strptime(value, fmt)
                            break
                        except ValueError:
                            continue
                    if parsed_value is None:
                        raise ValueError(f"Не вдалося розпізнати формат дати: {value}")
                    data_dict[col_name] = parsed_value
                else:
                    data_dict[col_name] = expected_type(value)
            session.add(model_class(**data_dict))
            session.commit()
            print(f"\nУспішно додано запис до {name_table}")
        except (ValueError, TypeError) as e:
            session.rollback()
            print(f"\n---!ERROR: Помилка типу даних. Не вдалося конвертувати значення: {e}")
            print("Перевірте, що вводите число для числових полів.")
        except IntegrityError as e:
            session.rollback()
            print("\n---!ERROR: Помилка цілісності даних.")
            print("Причина: Або такий Primary Key (ID) вже існує, або Foreign Key (ID), на який ви посилаєтесь, не існує.")
            print(f"---!DEBUG: {e.orig}") # e.orig покаже оригінальну помилку від PostgreSQL
        except Exception as e:
            session.rollback()
            print(f"\n---!ERROR: Загальна помилка при додаванні до {name_table}: {e}")
        input("Натисніть Enter для продовження...")

    def delete_table_data(self, name_table: str, conditions: str):
        model_class = self.models.get(name_table)
        if not model_class:
            print(f"---!ERROR: Модель з іменем '{name_table}' не знайдена.")
            input("Натисніть Enter для продовження...")
            return
        try:
            # Створюємо запит для видалення
            query = session.query(model_class)
        
            # Парсимо умови WHERE
            if conditions and conditions.strip() != '':
                conditions_parts = conditions.split(',')
                for part in conditions_parts:
                    part = part.strip()
                    if not part:
                        continue
                
                    match = re.match(r"^\s*(\w+)\s*([<>=])\s*(.+)\s*$", part)
                    if not match:
                        print(f"# -> ПОПЕРЕДЖЕННЯ: Некоректний формат умови '{part}'. Пропускаємо.")
                        continue
                
                    col_name = match.group(1).strip()
                    op = match.group(2).strip()
                    value_str = match.group(3).strip().strip("'\"")
                
                    # Отримуємо колонку з моделі
                    if not hasattr(model_class, col_name):
                        print(f"---!ERROR: Колонка '{col_name}' не знайдена в таблиці '{name_table}'.")
                        input("Натисніть Enter для продовження...")
                        return
                
                    col_obj = getattr(model_class, col_name)
                
                    # Визначаємо тип колонки та конвертуємо значення
                    col_type = col_obj.property.columns[0].type
                    try:
                        python_type = col_type.python_type
                        if python_type == datetime:
                            # Обробка datetime
                            match_dt = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})([+-]\d{2})$', value_str)
                            if match_dt:
                                value_str = match_dt.group(1) + match_dt.group(2) + ':00'
                            formats = ['%Y-%m-%d %H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
                            typed_value = None
                            for fmt in formats:
                                try:
                                    typed_value = datetime.strptime(value_str, fmt)
                                    break
                                except ValueError:
                                    continue
                            if typed_value is None:
                                typed_value = value_str
                        elif python_type != str:
                            typed_value = python_type(value_str)
                        else:
                            typed_value = value_str
                    except (ValueError, TypeError, NotImplementedError):
                        typed_value = value_str
                
                    # Застосовуємо фільтр
                    if op == '=':
                        query = query.filter(col_obj == typed_value)
                    elif op == '>':
                        query = query.filter(col_obj > typed_value)
                    elif op == '<':
                        query = query.filter(col_obj < typed_value)
            else:
                print("---!ERROR: Умова WHERE обов'язкова для видалення!")
                input("Натисніть Enter для продовження...")
                return
        
            # Виконуємо видалення
            deleted_count = query.delete()
            session.commit()
            print(f"\n✓ Успішно видалено {deleted_count} запис(ів) з таблиці {name_table}")
        
        except IntegrityError as e:
            session.rollback()
            print("\n---!ERROR: Помилка цілісності даних при видаленні.")
            print("Можливо, на цей запис посилаються інші таблиці (Foreign Key constraint).")
            print(f"---!DEBUG: {e.orig}")
        except Exception as e:
            session.rollback()
            print(f"\n---!ERROR: Помилка при видаленні з {name_table}: {e}")
    
        input("Натисніть Enter для продовження...")


    def update_table_data(self, name_table: str, columns: str, values: str, conditions: str):
        model_class = self.models.get(name_table)
        if not model_class:
            print(f"---!ERROR: Модель з іменем '{name_table}' не знайдена.")
            input("Натисніть Enter для продовження...")
            return
        try:
            # Парсимо колонки та значення
            columns_list = [col.strip() for col in columns.split(',')]
            values_list = [val.strip() for val in values.split(',')]
            if len(columns_list) != len(values_list):
                print(f"---!ERROR: Кількість колонок ({len(columns_list)}) не збігається з кількістю значень ({len(values_list)}).")
                input("Натисніть Enter для продовження...")
                return
            # Створюємо запит для оновлення
            query = session.query(model_class)
            # Парсимо умови WHERE
            if conditions and conditions.strip() != '':
                conditions_parts = conditions.split(',')
                for part in conditions_parts:
                    part = part.strip()
                    if not part:
                        continue
                    match = re.match(r"^\s*(\w+)\s*([<>=])\s*(.+)\s*$", part)
                    if not match:
                        print(f"# -> ПОПЕРЕДЖЕННЯ: Некоректний формат умови '{part}'. Пропускаємо.")
                        continue
                    col_name = match.group(1).strip()
                    op = match.group(2).strip()
                    value_str = match.group(3).strip().strip("'\"")
                
                    if not hasattr(model_class, col_name):
                        print(f"---!ERROR: Колонка '{col_name}' не знайдена в таблиці '{name_table}'.")
                        input("Натисніть Enter для продовження...")
                        return
                
                    col_obj = getattr(model_class, col_name)
                    col_type = col_obj.property.columns[0].type
                
                    try:
                        python_type = col_type.python_type
                        if python_type == datetime:
                            match_dt = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})([+-]\d{2})$', value_str)
                            if match_dt:
                                value_str = match_dt.group(1) + match_dt.group(2) + ':00'
                            formats = ['%Y-%m-%d %H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
                            typed_value = None
                            for fmt in formats:
                                try:
                                    typed_value = datetime.strptime(value_str, fmt)
                                    break
                                except ValueError:
                                    continue
                            if typed_value is None:
                                typed_value = value_str
                        elif python_type != str:
                            typed_value = python_type(value_str)
                        else:
                            typed_value = value_str
                    except (ValueError, TypeError, NotImplementedError):
                        typed_value = value_str
                
                    if op == '=':
                        query = query.filter(col_obj == typed_value)
                    elif op == '>':
                        query = query.filter(col_obj > typed_value)
                    elif op == '<':
                        query = query.filter(col_obj < typed_value)
            else:
                print("---!ERROR: Умова WHERE обов'язкова для оновлення!")
                input("Натисніть Enter для продовження...")
                return
        
            # Формуємо словник для оновлення
            update_dict = {}
            for col_name, value in zip(columns_list, values_list):
                if not hasattr(model_class, col_name):
                    print(f"---!ERROR: Колонка '{col_name}' не знайдена в таблиці '{name_table}'.")
                    input("Натисніть Enter для продовження...")
                    return
            
                col_obj = getattr(model_class, col_name)
                col_type = col_obj.property.columns[0].type
            
                try:
                    python_type = col_type.python_type
                    if python_type == datetime:
                        match_dt = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})([+-]\d{2})$', value)
                        if match_dt:
                            value = match_dt.group(1) + match_dt.group(2) + ':00'
                        formats = ['%Y-%m-%d %H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
                        parsed_value = None
                        for fmt in formats:
                            try:
                                parsed_value = datetime.strptime(value, fmt)
                                break
                            except ValueError:
                                continue
                        if parsed_value is None:
                            raise ValueError(f"Не вдалося розпізнати формат дати: {value}")
                        update_dict[col_obj] = parsed_value
                    elif python_type != str:
                        update_dict[col_obj] = python_type(value)
                    else:
                        update_dict[col_obj] = value
                except (ValueError, TypeError, NotImplementedError) as e:
                    print(f"---!ERROR: Помилка конвертації значення '{value}' для колонки '{col_name}': {e}")
                    input("Натисніть Enter для продовження...")
                    return
        
            # Виконуємо оновлення
            updated_count = query.update(update_dict)
            session.commit()
            print(f"\n✓ Успішно оновлено {updated_count} запис(ів) в таблиці {name_table}")
        
        except IntegrityError as e:
            session.rollback()
            print("\n---!ERROR: Помилка цілісності даних при оновленні.")
            print("Можливо, ви намагаєтесь встановити Primary Key, який вже існує, або Foreign Key, який не існує.")
            print(f"---!DEBUG: {e.orig}")
        except Exception as e:
            session.rollback()
            print(f"\n---!ERROR: Помилка при оновленні {name_table}: {e}")
    
        input("Натисніть Enter для продовження...")

    def get_table_data(self, name_table: str, columns: list, number_rows: str, order: list, conditions: str):
        metadata = MetaData()
        self.need_columns = []
        self.gotten_data = []
        # FROM
        table = Table(name_table, metadata, autoload_with = engine)
        # SELECT
        if columns == ['ALL']:
            columns = [column.name for column in table.columns]
            columns_to_get = [table.c[column] for column in columns]
        else:
            columns_to_get = [table.c[column] for column in columns]
        query = session.query(*columns_to_get)
        # WHERE
        filter_list = []
        if conditions != 'NONE':
            conditions_parts = conditions.split(',')
            for part in conditions_parts:
                part = part.strip()
                if not part:
                    continue
                match = re.match(r"^\s*(\w+)\s*([<>=])\s*(.+)\s*$", part)
                if not match:
                    print(f"# -> ПОПЕРЕДЖЕННЯ: Некоректний формат умови '{part}'. Пропускаємо.")
                    continue
                col_name = match.group(1).strip()
                op = match.group(2).strip()
                value_str = match.group(3).strip().strip("'\"")
                if col_name not in table.c:
                    raise KeyError(f"Колонка '{col_name}' не знайдена в таблиці '{table.name}'.")
                col_obj = table.c[col_name]
                typed_value = value_str
                try:
                    python_type = col_obj.type.python_type
                    if python_type != str:
                        typed_value = python_type(value_str)
                except (ValueError, TypeError):
                    print(f"# -> ПОПЕРЕДЖЕННЯ: Не вдалося конвертувати '{value_str}' в тип {python_type} для колонки '{col_name}'.")
                except NotImplementedError:
                    pass
                if op == '=':
                    filter_list.append(col_obj == typed_value)
                elif op == '>':
                    filter_list.append(col_obj > typed_value)
                elif op == '<':
                    filter_list.append(col_obj < typed_value)         
        query = query.filter(*filter_list)
        # ORDER
        if order != ['NONE']:
            order_by_list = [table.c[column] for column in order]
        else:
            order_by_list = []
        query = query.order_by(*order_by_list)
        # LIMIT
        if number_rows != 'ALL':
            query = query.limit(int(number_rows))
        self.need_columns = columns
        self.gotten_data = query.all()

    def analysis_table_data(self) -> tuple:
        return self.need_columns, self.gotten_data