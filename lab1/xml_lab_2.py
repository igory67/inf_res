#pip install xml_python

import xml.etree.ElementTree as et

tree = et.parse('a_groups.xml')
root = tree.getroot()

objects = root.findall('another-students-db-a-group')

#TASK 2A

atr_names = []
for atr in objects[0]:
    atr_names.append(atr.tag)

print(' Collected atributes: ')
for name in atr_names:
    print(f' - {name}')

#TASK 2B

fields_w_constraints = dict()
for object in objects:
    for element in object:
        tag_name = element.tag
        xml_type = element.get('type')

        if xml_type is None:
            xml_type = 'string'
        value = element.text

        if tag_name not in fields_w_constraints.keys():
            fields_w_constraints[tag_name] = {
                "type": xml_type,
                "not_null": value is not None,
                "possible_values": set()
            }
        
        if xml_type == "string": 
            current_max = fields_w_constraints[tag_name]["max_len"] if "max_len" in fields_w_constraints[tag_name] else -1
            current_len = 0 if value is None else len(value)
            fields_w_constraints[tag_name]["max_len"] = max(current_max, current_len)

        if fields_w_constraints[tag_name]["not_null"]:
            fields_w_constraints[tag_name]["not_null"] = value is not None
        
        if len(fields_w_constraints[tag_name]["possible_values"]) < 6:
            fields_w_constraints[tag_name]["possible_values"].add(value)

#print(fields_w_constraints)
print('Поля:\n')
for field, data in fields_w_constraints.items():
    print(f"Поле: {field}")
    print(f'\tТип данных: {data["type"]}')
    if "max_len" in data:
        print(f'\tМаксимальная длина строки: {data["max_len"]}')
    print(f"\tНеобходимо поставить NOT_NULL: {'Да' if data['not_null'] else 'Нет'}")
    print(f'count of possible values = {len(data["possible_values"])}')
    if 2 <= len(data["possible_values"]) <= 5:
        print(f"\tCHECK ({field} in ({', '.join(data['possible_values'])}))")


# TASK 3
"""
CREATE TABLE another_students_db_a_group (
    id INTEGER PRIMARY KEY,
    name VARCHAR(11) NOT NULL,
    old_name VARCHAR(8),
    term_number INTEGER NOT NULL,
    study_year VARCHAR(9) NOT NULL,
    created_at DATE NOT NULL,
    updated_at DATE NOT NULL
);
"""