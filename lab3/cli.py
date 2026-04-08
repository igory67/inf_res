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
    per_page = 20  # дефолт значение
    
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


def check_year(year):
    if year < 1985 or year > 2016:
        print("Ошибка: год должен быть в диапазоне 1985-2016.")
        return False
    return True

def check_int(number):
    if number <= 0:
        return False
    return True

def check_sex(sex):
    if sex not in ('male', 'female'):
        print("Ошибка: пол должен быть 'male' или 'female'.")
        return False
    return True

def check_age(age):
    valid_ages = ['5-14 years', '15-24 years', '25-34 years', 
                  '35-54 years', '55-74 years', '75+ years']
    
    if age not in valid_ages:
        print(f"Ошибка: возрастная группа '{age}' недопустима.")
        print(f"Допустимые значения: {', '.join(valid_ages)}")
        return False
    return True

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
        
        country = country[:30]

        if not check_year(year):
            #print("Ошибка: год должен быть в диапазоне 1985-2016.")
            return
            
        population = int(population)
        if not check_int(population) and not check_empty(population):
            print("Ошибка: население должно быть больше 0.")
            return
            
        suicides_no = int(suicides_no)
        if not check_int(suicides_no) and not check_empty(suicides_no):
            print("Ошибка: число суицидов не может быть отрицательным.")
            return
            
        suicides_100k_pop = float(suicides_100k_pop)
        if not check_int(suicides_100k_pop) and not check_empty(suicides_100k_pop):
            print("Ошибка: показатель суицидов не может быть отрицательным.")
            return
        
    except ValueError:
        print("Ошибка: проверьте типы данных (год, население, суициды - целые числа, показатель - число).")
        return

    if not check_sex(sex) and not check_empty(sex):
        # print("Ошибка: пол должен быть 'male' или 'female'.")
        return
    
    if not check_age(age) and not check_empty(age): # not in valid_ages:
        # print(f"Ошибка: возрастная группа '{age}' недопустима.")
        # print(f"Допустимые значения: {', '.join(valid_ages)}")
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

def check_id(rid):
    if not rid:
        print("ID не должен быть пустым")
        return False
    
    try:
        resp = requests.get(f"{BASE_URL}/suicides/{rid}")
        if resp.status_code == 404:
            print("нет такой записи ")
            return False
        elif resp.status_code != 200:
            print(f"возникла Ошибка при проверке id: {resp.status_code}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка {e}")
        return False
    # return True

def check_empty(attr):
    if not attr:
        print("Не может быть пустой строкой")
        return False
    return True 

def update_record():
    
    rid = input("ID записи для обновления: ").strip()
    if not check_id(rid):
        #print("ID не может быть пустым.")
        return
    
    chosen_changes = {}

    while (True):
        print("Что хотите поменять? " \
        "0 - выход" \
        "1 - country" \
        "2 - year" \
        "3 - sex" \
        "4 - age" \
        "5 - suicides_no" \
        "6 - population" \
        "7 - suicides/100k pop")
        decision = input("Выбор: ").strip()
        if decision == 0:
            break

        elif decision == 1:
            country = input("Введите название страные (длина <= 30)").strip()
            if not check_empty(country):
                continue
            country = country[:30]
            chosen_changes["country"] = country

        elif decision == 2:
            year = input("Год (year, 1985-2016): ").strip()
            try:
                year = int(year)
                if not check_year(year):
                    continue
                chosen_changes["year"] = year
            except ValueError:
                print("Ошибка с типами данных в числах.")
                continue 
        elif decision == "3":
            sex = input("Пол (male/female): ").strip().lower()
            if not check_sex(sex):
                continue
            chosen_changes["sex"] = sex
            
        elif decision == "4":
            valid_ages = ['5-14 years', '15-24 years', '25-34 years', 
                            '35-54 years', '55-74 years', '75+ years']
            print(f"Возрастные группы (age): {', '.join(valid_ages)}")
            age = input("Возрастная группа: ").strip()
            try:
                age = int(age)
                if not check_age(age):
                    continue
                chosen_changes["age"] = age
            except ValueError:
                print("Ошибка с типами данных в числах.")
                continue 
        elif decision == "5":
            suicides_str = input("Число суицидов (suicides_no, >=0): ").strip() 
            try:
                suicides_no = int(suicides_str)
                if not check_int(suicides_no) and not check_empty(suicides_no):
                    continue
                chosen_changes["suicides_no"] = suicides_no
            except ValueError:
                print("Ошибка с типами данных в числах.")
                continue 
        elif decision == "6":
            pop_str = input("Население (population, >0): ").strip()
            try:
                population = int(pop_str)
                if not check_int(population) and not check_empty(population):
                    continue
                chosen_changes["population"] = population
            except ValueError:
                print("Ошибка с типами данных в числах.")
                continue 
        elif decision == "7":
            rate_str = input("Суицидов на 100k населения (suicides_100k_pop, >=0): ").strip()
            try:
                rate = float(rate_str)
                if not check_int(rate):
                    continue
                chosen_changes["suicides_100k_pop"] = rate
            except ValueError:
                print("Ошибка с типами данных в числах.")
                continue 
        else:
            continue

        # '', 'year', 'sex', 'age', 'suicides_no', 'population', 'suicides/100k pop'
    # print("Введите обновляемые поля в JSON (можно не все, например {\"suicides_no\": 600})")
    # data_str = input("JSON: ").strip()
    # try:
    #     data = json.loads(data_str)
    # except json.JSONDecodeError:
    #     print("Ошибка: неверный JSON.")
    #     return
    resp = requests.put(f"{BASE_URL}/suicides/{rid}", json=chosen_changes)
    print_response(resp)


def delete_record():
    
    rid = input("ID записи для удаления: ").strip()
    if not check_id(rid):
        #print("ID не может быть пустым.")
        return
    resp = requests.delete(f"{BASE_URL}/suicides/{rid}")
    print_response(resp)
    return

def total_by_year():
    
    year = input("Год: ").strip()
    try:
        year = int(year)
        if not check_year(year):
            return
    except: 
        print("Ошибка с типами данных в числах.")
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