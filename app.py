from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, init_app
from flask_migrate import Migrate
from database.models import Task, User
from flask_login import current_user
import psycopg2
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Cambia el backend a un backend no interactivo
import matplotlib.pyplot as plt
import os


    
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tasks_user:123456@localhost/tasks_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not os.path.exists('static/images'):
    os.makedirs('static/images')

# Inicializar la base de datos
db.init_app(app)

# Inicializa Flask-Migrate
migrate = Migrate(app, db)

# Configura Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    print(f"Usuario autenticado: {current_user.is_authenticated}")  # Verifica si el usuario está autenticado

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    filter_value = request.args.get('filter', '')
    tasks_query = Task.query.filter_by(user_id=current_user.id)

    if filter_value == 'completed':
        tasks_query = tasks_query.filter_by(completed=True)
    elif filter_value == 'pending':
        tasks_query = tasks_query.filter_by(completed=False)

    tasks = tasks_query.all()

    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task.completed])
    pending_tasks = total_tasks - completed_tasks
    progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    return render_template(
        'tasks.html',
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        progress=progress,
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Depuración: Imprime los datos en la consola
        print(f"Usuario: {username}, Email: {email}, Contraseña: {password}")

        if not username or not email or not password:
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado.', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)  # Asegúrate de que este método existe y funciona
            db.session.add(user)
            db.session.commit()
            flash('Usuario registrado exitosamente. Inicia sesión.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/actualizar-datos')
def actualizar_datos():
    conn_params = {
        "host": "localhost",
        "database": "tasks_db",
        "user": "tasks_user",
        "password": "123456"
    }
    with psycopg2.connect(**conn_params) as conn:
        df = pd.read_sql("SELECT * FROM Task", conn)
    
    return jsonify(df.to_dict(orient="records"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos.', 'error')
    return render_template('login.html')



@app.route('/some_route')
def some_route():
    if current_user.is_authenticated:
        user_id = current_user.id
        # Lógica cuando el usuario está autenticado
    else:
        # Redirigir o manejar usuarios no autenticados
        return redirect(url_for('login'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('login'))

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    new_task = Task(title=title, description=description, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()

    generate_graphs()
    return redirect('/')

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed
        db.session.commit()
        generate_graphs()
        return jsonify({'success': True, 'completed': task.completed})
    return jsonify({'success': False}), 404



@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        generate_graphs()
        return jsonify(success=True)
    return jsonify(success=False), 404


@app.route('/delete_all_tasks', methods=['POST'])
def delete_all_tasks():
    try:
        Task.query.delete()  # Elimina todas las tareas de la base de datos
        db.session.commit()  # Guarda los cambios
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()  # Revierte si hay error
        return jsonify({"success": False, "error": str(e)}), 500
    
    
@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').strip()
    if query:
        results = Task.query.filter(
            Task.title.ilike(f'%{query}%'),
            Task.user_id == current_user.id
        ).all()
        return jsonify({
            'results': [{'id': task.id, 'title': task.title} for task in results]
        })
    return jsonify({'results': []})



@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()

    # Depuración: Verifica si hay tareas en la base de datos
    print(f"Tareas encontradas: {tasks}")

    generate_graphs()

    return jsonify({
        'tasks': [{'id': task.id, 'title': task.title, 'description': task.description, 'completed': task.completed, 'date_added': task.date_added.strftime('%Y-%m-%d')} for task in tasks]
    })



@app.route('/load_more', methods=['GET'])
def load_more_tasks():
    offset = int(request.args.get('offset', 0))
    limit = 6  # Número de tareas a cargar por cada "Ver Más"
    
    tasks = Task.query.offset(offset).limit(limit).all()
    total_tasks = Task.query.count()

    tasks_data = [{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "date_added": task.date_added.strftime('%Y-%m-%d')
    } for task in tasks]

    has_more = (offset + limit) < total_tasks

    return jsonify({
        "tasks": tasks_data,
        "hasMore": has_more
    })

def generate_graphs():
    tasks = Task.query.all()
    data = [{"completed": task.completed, "date_added": task.date_added} for task in tasks]
    df = pd.DataFrame(data)

    completed_count = df['completed'].sum()
    pending_count = len(df) - completed_count
    labels = ['Completadas', 'Pendientes']
    values = [completed_count, pending_count]

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#4CAF50', '#F44336'])
    plt.title('Distribución de Tareas')
    plt.savefig('static/images/distribution_of_tasks.png')
    plt.close()

    if not df.empty and 'date_added' in df.columns:
        df['date_added'] = pd.to_datetime(df['date_added'])
        tasks_per_day = df.groupby(df['date_added'].dt.date).size()

        plt.figure(figsize=(10, 6))
        tasks_per_day.plot(kind='bar', color='skyblue')
        plt.title('Tareas Creadas por Día')
        plt.xlabel('Fecha')
        plt.ylabel('Número de Tareas')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('static/images/tasks_per_day.png')
        plt.close()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos creada exitosamente.")

    app.run(debug=True)

