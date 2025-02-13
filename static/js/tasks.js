// Marcar una tarea como completada o pendiente
function toggleTask(taskId) {
    fetch(`/update/${taskId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.reload();
        } else {
            alert('Error al actualizar la tarea.');
        }
    });
}

// Eliminar una tarea
function deleteTask(taskId) {
    fetch(`/delete/${taskId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.reload();
        } else {
            alert('Error al eliminar la tarea.');
        }
    });
}
