from app import db
from flask import Blueprint, request, jsonify, render_template, session, redirect
from functools import wraps
from app.models import User
from werkzeug.security import generate_password_hash
from sqlalchemy import or_

superadmin_routes = Blueprint(
    "superadmin_routes",
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/superadmin/static'
)


@superadmin_routes.context_processor
def inject_user():
    return {"table_names": db.metadata.tables.keys()}


def superadmin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/superadmin/login")
        return f(*args, **kwargs)
    return decorated_function


@superadmin_routes.route("/superadmin/login", methods=["GET", "POST"])
def superadmin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect("/superadmin/table/users")
        return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")


@superadmin_routes.route("/superadmin/logout", methods=["GET"])
@superadmin_login_required
def superadmin_logout():
    session.clear()
    return redirect("/superadmin/login")


@superadmin_routes.route("/superadmin/table/<table_name>", methods=["GET"])
@superadmin_login_required
def superadmin_table(table_name):
    if table_name not in db.metadata.tables:
        return "Table not found", 404

    table = db.metadata.tables[table_name]
    columns = [column.name for column in table.columns]
    
    # column_types ve enum_values'u al
    column_types, enum_values = get_column_types(table)

    query = db.session.query(table).all()

    return render_template(
        "main.html",
        table_name=table_name,
        columns=columns,
        table_data=query,
        column_types=column_types,  # column_types'ı template'e gönder
        enum_values=enum_values     # enum_values'u da gönder
    )


def get_column_types(table):
    column_types = {}
    enum_values = {}
    
    for column in table.columns:
        # SQLAlchemy tipi string'e çevirip kontrol ediyoruz
        type_str = str(column.type).lower()
        
        if 'boolean' in type_str:
            column_types[column.name] = 'boolean'
        elif 'enum' in type_str:
            column_types[column.name] = 'enum'
            # Enum değerlerini alıyoruz
            enum_values[column.name] = [e.name for e in column.type.enums]
        else:
            column_types[column.name] = 'text'
    
    return column_types, enum_values


def handle_password_field(data, table):
    """Eğer password alanı varsa şifrele"""
    if 'password' in data and data['password']:
        data['password'] = generate_password_hash(data['password'])
    return data


@superadmin_routes.route("/superadmin/table/<table_name>/add", methods=["GET", "POST"])
@superadmin_login_required
def add_item(table_name):
    if table_name not in db.metadata.tables:
        return "Table not found", 404

    table = db.metadata.tables[table_name]
    columns = [column.name for column in table.columns]
    column_types, enum_values = get_column_types(table)

    if request.method == "POST":
        data = {}
        for column in columns:
            if column != 'id':
                if column_types[column] == 'boolean':
                    data[column] = request.form.get(column) == 'on'
                else:
                    value = request.form.get(column)
                    if value:
                        data[column] = value
        
        # Şifre alanı varsa şifrele
        data = handle_password_field(data, table)
        
        stmt = table.insert().values(**data)
        db.session.execute(stmt)
        db.session.commit()
        
        return redirect(f"/superadmin/table/{table_name}")

    return render_template("form.html", 
                         table_name=table_name, 
                         columns=columns, 
                         action="Add",
                         item=None,
                         column_types=column_types,
                         enum_values=enum_values)


@superadmin_routes.route("/superadmin/table/<table_name>/edit/<int:id>", methods=["GET", "POST"])
@superadmin_login_required
def edit_item(table_name, id):
    if table_name not in db.metadata.tables:
        return "Table not found", 404

    table = db.metadata.tables[table_name]
    columns = [column.name for column in table.columns]
    column_types, enum_values = get_column_types(table)
    
    item = db.session.query(table).filter_by(id=id).first()
    if not item:
        return "Item not found", 404

    if request.method == "POST":
        data = {}
        for column in columns:
            if column != 'id':
                if column_types[column] == 'boolean':
                    data[column] = request.form.get(column) == 'on'
                else:
                    value = request.form.get(column)
                    if value:
                        data[column] = value
        
        # Şifre alanı varsa şifrele
        data = handle_password_field(data, table)
        
        stmt = table.update().where(table.c.id == id).values(**data)
        db.session.execute(stmt)
        db.session.commit()
        
        return redirect(f"/superadmin/table/{table_name}")

    return render_template("form.html", 
                         table_name=table_name, 
                         columns=columns, 
                         action="Edit",
                         item=item,
                         column_types=column_types,
                         enum_values=enum_values)


@superadmin_routes.route("/superadmin/table/<table_name>/delete/<int:id>", methods=["POST"])
@superadmin_login_required
def delete_item(table_name, id):
    if table_name not in db.metadata.tables:
        return "Table not found", 404

    table = db.metadata.tables[table_name]
    stmt = table.delete().where(table.c.id == id)
    db.session.execute(stmt)
    db.session.commit()
    
    return jsonify({"success": True})


@superadmin_routes.route("/superadmin/table/<table_name>/delete-multiple", methods=["POST"])
@superadmin_login_required
def delete_multiple(table_name):
    if table_name not in db.metadata.tables:
        return "Table not found", 404

    ids = request.json.get('ids', [])
    table = db.metadata.tables[table_name]
    stmt = table.delete().where(table.c.id.in_(ids))
    db.session.execute(stmt)
    db.session.commit()
    
    return jsonify({"success": True})


@superadmin_routes.route("/superadmin/table/<table_name>/quick-update/<int:id>", methods=["POST"])
@superadmin_login_required
def quick_update(table_name, id):
    if table_name not in db.metadata.tables:
        return "Table not found", 404

    table = db.metadata.tables[table_name]
    data = request.json
    
    # Güncelleme verilerini hazırla
    update_data = {data['column']: data['value']}
    
    # Şifre alanı varsa şifrele
    update_data = handle_password_field(update_data, table)
    
    stmt = table.update().where(table.c.id == id).values(**update_data)
    db.session.execute(stmt)
    db.session.commit()
    
    return jsonify({"success": True})


@superadmin_routes.route("/superadmin/table/<table_name>/search")
@superadmin_login_required
def search_table(table_name):
    if table_name not in db.metadata.tables:
        return "Table not found", 404

    search_term = request.args.get('term', '').strip()
    table = db.metadata.tables[table_name]
    columns = [column.name for column in table.columns]
    column_types, _ = get_column_types(table)

    # Arama kriterlerini oluştur
    search_criteria = []
    for column in columns:
        if column_types[column] != 'boolean':  # Boolean alanları aramaya dahil etme
            search_criteria.append(
                table.c[column].cast(db.String).ilike(f'%{search_term}%')
            )

    # Arama yap
    if search_term:
        query = db.session.query(table).filter(or_(*search_criteria))
    else:
        query = db.session.query(table)

    results = query.all()
    
    # HTML oluştur
    html = render_template(
        "table_rows.html",
        table_data=results,
        columns=columns,
        column_types=column_types,
        table_name=table_name
    )
    
    return jsonify({"html": html})
