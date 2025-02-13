from database import db
from database.models import Task
from app import app

def delete_all_tasks():
    with app.app_context():
        try:
            db.session.query(Task).delete()  # Método más seguro para eliminar todas las tareas
            db.session.commit()
            print("✅ Todas las tareas han sido eliminadas correctamente.")
        except Exception as e:
            db.session.rollback()  # Si hay un error, revierte la operación
            print(f"❌ Error al eliminar tareas: {e}")

if __name__ == "__main__":
    delete_all_tasks()
