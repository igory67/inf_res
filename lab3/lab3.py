from flask import Flask, request, jsonify
from bd_maker import Connector
import os
 
app = Flask(__name__)

def get_db():
    return Connector()
 
 
def rows_to_list(db, rows):
    cols = db.columns()
    return [dict(zip(cols, row)) for row in rows]
 
 
def _to_xml(tag, records):
    items = ""
    for r in records:
        fields = "".join(f"<{k}>{v}</{k}>" for k, v in r.items())
        items += f"<{tag}>{fields}</{tag}>"
    return f'<?xml version="1.0" encoding="UTF-8"?><response>{items}</response>'
 
 
def respond(data, fmt, code=200, tag="record"):
    if fmt == "wsdl":
        records = data if isinstance(data, list) else [data]
        return _to_xml(tag, records), code, {"Content-Type": "text/xml"}
    return jsonify(data), code


#task 1a
@app.route("/suicides", methods=["GET"])
def list_suicides():
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(int(request.args.get("per_page", 20)), 100))
    offset = (page - 1) * per_page
    fmt = request.args.get("format", "json").lower()
 
    db = get_db()
    table = db.suic_table_name()
 
    total_rows = db.sql_execute(f"SELECT COUNT(*) FROM {table}")
    total = total_rows[0][0] if total_rows else 0
 
    rows = db.sql_execute(
        f"SELECT {', '.join(db.columns())} FROM {table} ORDER BY id LIMIT %s OFFSET %s",
        [per_page, offset]
    )
 
    data = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page,
        "data": rows_to_list(db, rows),
    }
 
    if fmt == "wsdl":
        return _to_xml("suicide", data["data"]), 200, {"Content-Type": "text/xml"}
    #return respond(data, fmt, tag='suicide')
    return jsonify(data)


#task 1b
@app.route("/suicides/<int:record_id>", methods=["GET"])
def get_suicide(record_id):
    fmt = request.args.get("format", "json").lower()
    db = get_db()
    table = db.suic_table_name()
 
    rows = db.sql_execute(
        f"SELECT {', '.join(db.columns())} FROM {table} WHERE id = %s",
        [record_id]
    )
 
    if not rows:
        return respond({"error": "Record not found"}, fmt, tag='response', code=404)
 
    record = dict(zip(db.columns(), rows[0]))
    return respond(record, fmt, tag="suicide")


#task 1c
@app.route("/suicides", methods=["POST"])
def create_suicide():
    body = request.get_json(force=True)
    fmt = request.args.get("format", "json").lower()
    db = get_db()
    missing = [f for f in ['country', 'year', 'sex', 'age', 'population', 'suicides_no', 'suicides_100k_pop'] if f not in body]
 
    if missing:
        return respond({"error": f"Missing required fields: {missing}"}, fmt, tag='response', code=404)
 
    values = [body.get(col) for col in db.columns_without_id()]
    db.taskb_insert_into_table(values)
 

    rows = db.sql_execute(
        f"SELECT {', '.join(db.columns())} FROM {db.suic_table_name()} "
        f"WHERE country=%s AND year=%s AND sex=%s AND age=%s "
        f"ORDER BY id DESC LIMIT 1",
        [body['country'], body['year'], body['sex'], body['age']]
    )
 
    if not rows:
        return respond({"message": "Record created"}, fmt, code=201, tag='response')
 
    record = dict(zip(db.columns(), rows[0]))
    #return jsonify(record), 201
    return respond(record, fmt, code=201)


#task 1d
@app.route("/suicides/<int:record_id>", methods=["PUT"])
def update_suicide(record_id):
    body = request.get_json(force=True)
    fmt = request.args.get("format", "json").lower()
    db = get_db()
    table = db.suic_table_name()
 
    existing = db.sql_execute(
        f"SELECT id FROM {table} WHERE id = %s", [record_id]
    )
    if not existing:
        #return jsonify({"error": "Record not found"}), 404
        return respond({"error": "Record not found"}, fmt,code=404)
 
    updatable = db.columns_without_id()
    updates = {k: v for k, v in body.items() if k in updatable}
 
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400
 
    set_expr = ", ".join(f"{k} = %s" for k in updates)
    values = list(updates.values()) + [record_id]
 
    db.sql_execute(
        f"UPDATE {table} SET {set_expr} WHERE id = %s", values
    )
 
    rows = db.sql_execute(
        f"SELECT {', '.join(db.columns())} FROM {table} WHERE id = %s",
        [record_id]
    )
    record = dict(zip(db.columns(), rows[0]))
    return respond(record, fmt, code=200)


#task 1e
@app.route("/suicides/<int:record_id>", methods=["DELETE"])
def delete_suicide(record_id):
    db = get_db()
    table = db.suic_table_name()
    fmt = request.args.get("format", "json").lower()
 
    existing = db.sql_execute(
        f"SELECT id FROM {table} WHERE id = %s", [record_id]
    )
    if not existing:
        return respond({"error": "Record not found"}, fmt, code=404)
 
    db.sql_execute(f"DELETE FROM {table} WHERE id = %s", [record_id])
    #return jsonify({"message": f"Record {record_id} deleted"}), 200
    return respond({"message": f"Record {record_id} deleted"}, fmt, code=200)


#task 1f 
@app.route("/suicides/total_by_year/<int:year>", methods=["GET"])
def total_suicides_by_year(year):
    fmt = request.args.get("format", "json").lower()
    db = get_db()
    table = db.suic_table_name()
    
    check_rows = db.sql_execute(
        f"SELECT COUNT(*) FROM {table} WHERE year = %s",
        [year]
    )
    
    if not check_rows or check_rows[0][0] == 0:
        return respond({
            "error": f"No data found for year {year}",
            "year": year
        }, fmt, tag='response', code=404)
    
    rows = db.sql_execute(
        f"SELECT SUM(suicides_no) as total_suicides FROM {table} WHERE year = %s",
        [year]
    )
    
    total = rows[0][0] if rows and rows[0][0] is not None else 0
    
    result = {
        "year": year,
        "total_suicides_worldwide": int(total)
    }
    
    return respond(result, fmt, tag='suicide_stats')


if __name__ == "__main__":
    #Connector().taska_creation()
    app.run(debug=True, port=5000)