import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def print_response(resp):

    print(f"\nСтатус: {resp.status_code}")
    try:
        if resp.headers.get('content-type', '').startswith('application/json'):
            data = resp.json()
            print("Ответ (JSON):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("Ответ (текст):")
            print(resp.text)
    except:
        print("Не удалось разобрать ответ")
    print()

def list_records():
    """GET /suicides с пагинацией (фиксировано 20 записей на страницу)."""
    page = input("Номер страницы (по умолчанию 1): ").strip()
    page = int(page) if page else 1
    per_page = 20  # фиксированное значение
    
    params = {"page": page, "per_page": per_page}
    resp = requests.get(f"{BASE_URL}/suicides", params=params)
    print_response(resp)


def get_record_by_id():

    rid = input("ID записи: ").strip()
    if not rid:
        print("ID не может быть пустым.")
        return
    resp = requests.get(f"{BASE_URL}/suicides/{rid}")
    print_response(resp)


def create_record():
    """POST /suicides с поочерёдным вводом полей."""
    valid_ages = ['5-14 years', '15-24 years', '25-34 years', 
                  '35-54 years', '55-74 years', '75+ years']
    
    print("Введите данные для новой записи (все поля обязательны):")
    country = input("Страна (country): ").strip()
    year = input("Год (year, 1985-2016): ").strip()
    sex = input("Пол (sex, male/female): ").strip().lower()
    
    print(f"Возрастные группы (age): {', '.join(valid_ages)}")
    age = input("Возрастная группа: ").strip()
    
    population = input("Население (population, >0): ").strip()
    suicides_no = input("Число суицидов (suicides_no, >=0): ").strip()
    suicides_100k_pop = input("Суицидов на 100k населения (suicides_100k_pop, >=0): ").strip()

    if not all([country, year, sex, age, population, suicides_no, suicides_100k_pop]):
        print("Ошибка: все поля должны быть заполнены.")
        return

    try:
        year = int(year)
        if year < 1985 or year > 2016:
            print("Ошибка: год должен быть в диапазоне 1985-2016.")
            return
            
        population = int(population)
        if population <= 0:
            print("Ошибка: население должно быть больше 0.")
            return
            
        suicides_no = int(suicides_no)
        if suicides_no < 0:
            print("Ошибка: число суицидов не может быть отрицательным.")
            return
            
        suicides_100k_pop = float(suicides_100k_pop)
        if suicides_100k_pop < 0:
            print("Ошибка: показатель суицидов не может быть отрицательным.")
            return
    except ValueError:
        print("Ошибка: проверьте типы данных (год, население, суициды - целые числа, показатель - число).")
        return

    if sex not in ('male', 'female'):
        print("Ошибка: пол должен быть 'male' или 'female'.")
        return
    
    if age not in valid_ages:
        print(f"Ошибка: возрастная группа '{age}' недопустима.")
        print(f"Допустимые значения: {', '.join(valid_ages)}")
        return

    data = {
        "country": country,
        "year": year,
        "sex": sex,
        "age": age,
        "population": population,
        "suicides_no": suicides_no,
        "suicides_100k_pop": suicides_100k_pop
    }

    resp = requests.post(f"{BASE_URL}/suicides", json=data)
    print_response(resp)

def update_record():
    
    rid = input("ID записи для обновления: ").strip()
    if not rid:
        print("ID не может быть пустым.")
        return
    print("Введите обновляемые поля в JSON (можно не все, например {\"suicides_no\": 600})")
    data_str = input("JSON: ").strip()
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        print("Ошибка: неверный JSON.")
        return
    resp = requests.put(f"{BASE_URL}/suicides/{rid}", json=data)
    print_response(resp)


def delete_record():
    
    rid = input("ID записи для удаления: ").strip()
    if not rid:
        print("ID не может быть пустым.")
        return
    resp = requests.delete(f"{BASE_URL}/suicides/{rid}")
    print_response(resp)


def total_by_year():
    
    year = input("Год: ").strip()
    if not year or not year.isdigit():
        print("Некорректный год.")
        return
    resp = requests.get(f"{BASE_URL}/suicides/total_by_year/{year}")
    print_response(resp)


def main():
    menu = {
        "1": ("Список записей (с пагинацией)", list_records),
        "2": ("Получить запись по ID", get_record_by_id),
        "3": ("Создать новую запись (POST)", create_record),
        "4": ("Обновить запись (PUT)", update_record),
        "5": ("Удалить запись (DELETE)", delete_record),
        "6": ("Суммарное число суицидов за год", total_by_year),
        "0": ("Выход", None)
    }
    
    while True:
        print("\n===== CLI для API суицидов =====")
        for key, (desc, _) in menu.items():
            print(f"{key}. {desc}")
        choice = input("Выберите действие: ").strip()
        
        if choice == "0":
            print("До свидания!")
            break
        elif choice in menu:
            action = menu[choice][1]
            if action:
                action()
            else:
                break
        else:
            print("Неверный ввод, попробуйте снова.")

if __name__ == "__main__":
    try:
        requests.get(f"{BASE_URL}/suicides", timeout=2)
    except requests.exceptions.ConnectionError:
        print("Ошибка: не удалось подключиться к серверу API.")
        print(f"Убедитесь, что сервер запущен на {BASE_URL} (например, запустите lab3.py)")
        sys.exit(1)
    main()