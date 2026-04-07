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
    
    page = input("Номер страницы (по умолчанию 1): ").strip()
    page = int(page) if page else 1
    per_page = input("Записей на странице (1-100, по умолчанию 20): ").strip()
    per_page = int(per_page) if per_page else 20
    per_page = max(1, min(per_page, 100))
    
    params = {"page": page, "per_page": per_page}
    # Можно добавить format, но по умолчанию JSON
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
    
    print("Введите данные в формате JSON (обязательные поля: country, year, sex, age, population, suicides_no, suicides_100k_pop)")
    print("Пример: {\"country\": \"Russia\", \"year\": 2020, \"sex\": \"male\", \"age\": \"25-34 years\", \"population\": 10000000, \"suicides_no\": 500, \"suicides_100k_pop\": 5.0}")
    data_str = input("JSON: ").strip()
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        print("Ошибка: неверный JSON.")
        return
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
    # Проверка доступности сервера
    try:
        requests.get(f"{BASE_URL}/suicides", timeout=2)
    except requests.exceptions.ConnectionError:
        print("Ошибка: не удалось подключиться к серверу API.")
        print(f"Убедитесь, что сервер запущен на {BASE_URL} (например, запустите lab3.py)")
        sys.exit(1)
    main()