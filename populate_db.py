import random
from faker import Faker
from database import db
from database.models import Task, User  # Importa User para asociar tareas a usuarios
from app import app

fake = Faker()

def generate_random_tasks(num_tasks=1000, user_id=None):
    """
    Genera tareas aleatorias y las inserta en la base de datos, asegurando que tengan un user_id.
    """
    with app.app_context():
        try:
            # Si no se proporciona user_id, tomar el primer usuario disponible en la base de datos
            if not user_id:
                first_user = User.query.first()  # Tomar un usuario existente
                if not first_user:
                    print("No hay usuarios en la base de datos. Crea un usuario primero.")
                    return
                user_id = first_user.id  # Asignar user_id al usuario encontrado
            
            tasks = []
            for _ in range(num_tasks):
                title = fake.sentence(nb_words=6)
                description = fake.paragraph(nb_sentences=3)
                completed = random.choice([True, False])
                date_added = fake.date_time_this_year()

                new_task = Task(
                    title=title,
                    description=description,
                    completed=completed,
                    date_added=date_added,
                    user_id=user_id  # 🔹 Asigna el usuario a la tarea
                )
                tasks.append(new_task)

            db.session.bulk_save_objects(tasks)
            db.session.commit()
            print(f"{num_tasks} tareas generadas exitosamente para el usuario con ID {user_id}.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al generar las tareas: {e}")

if __name__ == "__main__":
    try:
        num_tasks = int(input("¿Cuántas tareas deseas generar? "))
        user_id = int(input("Ingrese el ID del usuario para asignar las tareas (déjalo vacío para el primer usuario): ") or 0)
        generate_random_tasks(num_tasks, user_id if user_id > 0 else None)
    except ValueError:
        print("Por favor, ingresa un número válido.")
