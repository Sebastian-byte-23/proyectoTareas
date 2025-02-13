// Inicializamos los contextos de los canvas
const ctxPie = document.getElementById('chartPie').getContext('2d');
const ctxBar = document.getElementById('chartBar').getContext('2d');
const ctxLine = document.getElementById('chartLine').getContext('2d');
const ctxTitle = document.getElementById('chartTitle').getContext('2d');

// Creamos las instancias de Chart.js para cada gráfico
let chartPie = new Chart(ctxPie, {
    type: 'pie',
    data: {
        labels: ['Completadas', 'Pendientes'],
        datasets: [{
            data: [0, 0],
            backgroundColor: ['#4CAF50', '#F44336']
        }]
    },
    options: { responsive: true }
});

let chartBar = new Chart(ctxBar, {
    type: 'bar',
    data: {
        labels: [], // Fechas
        datasets: [{
            label: 'Número de Tareas',
            data: [],
            backgroundColor: 'rgba(54, 162, 235, 0.6)'
        }]
    },
    options: {
        responsive: true,
        scales: { y: { beginAtZero: true } }
    }
});

let chartLine = new Chart(ctxLine, {
    type: 'line',
    data: {
        labels: [], // Fechas
        datasets: [{
            label: 'Progreso (%)',
            data: [],
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: true,
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        scales: { y: { beginAtZero: true, max: 100 } }
    }
});

let chartTitle = new Chart(ctxTitle, {
    type: 'bar',
    data: {
        labels: ['<10', '10-20', '20-30', '30-40', '40+'],
        datasets: [{
            label: 'Cantidad de Tareas',
            data: [0, 0, 0, 0, 0],
            backgroundColor: 'rgba(153, 102, 255, 0.6)'
        }]
    },
    options: {
        responsive: true,
        scales: { y: { beginAtZero: true } }
    }
});


document.addEventListener('DOMContentLoaded', function() {
    fetch('/')  // Cambia esta URL si es necesario
        .then(response => {
            // Verifica el tipo de respuesta
            if (!response.ok) {
                throw new Error(`Error en la respuesta: ${response.status}`);
            }
            return response.text();  // Leer la respuesta como texto para inspeccionarla
        })
        .then(text => {
            console.log(text);  // Imprimir la respuesta completa para depurar
            try {
                const data = JSON.parse(text);  // Intentar parsear como JSON
                document.getElementById('totalTasks').innerText = data.total_tasks;
                document.getElementById('completedTasks').innerText = data.completed_tasks;
                document.getElementById('pendingTasks').innerText = data.pending_tasks;
            } catch (e) {
                console.error('Error al parsear la respuesta como JSON:', e);
            }
        })
        .catch(error => console.error('Error al cargar los datos:', error));
});


// Función para procesar los datos y actualizar los gráficos
async function actualizarDatosYGraficos() {
    try {
        // Si tu endpoint requiere user_id, se puede incluir en la URL (por ejemplo, user_id=123)
        const response = await fetch('/actualizar-datos?user_id');
        const data = await response.json();

        // Procesamiento general de datos
        const totalTasks = data.length;
        const completedTasks = data.filter(task => task.completed).length;
        const pendingTasks = totalTasks - completedTasks;

        // Actualizar gráfico Pie: Distribución de Tareas
        chartPie.data.datasets[0].data = [completedTasks, pendingTasks];
        chartPie.update();

        // Gráfico Bar: Tareas por Día (agrupamos por 'date_added')
        let tasksPerDay = {};
        data.forEach(task => {
            // Convertir fecha y formatear
            let date = new Date(task.date_added).toLocaleDateString();
            tasksPerDay[date] = (tasksPerDay[date] || 0) + 1;
        });
        const sortedDates = Object.keys(tasksPerDay).sort((a, b) => new Date(a) - new Date(b));
        const tasksCounts = sortedDates.map(date => tasksPerDay[date]);
        chartBar.data.labels = sortedDates;
        chartBar.data.datasets[0].data = tasksCounts;
        chartBar.update();

        // Gráfico Line: Progreso de Tareas a lo Largo del Tiempo
        // Calculamos el porcentaje de tareas completadas por día
        let progressPerDay = {};
        let tasksCountPerDay = {};
        data.forEach(task => {
            let date = new Date(task.date_added).toLocaleDateString();
            progressPerDay[date] = (progressPerDay[date] || 0) + (task.completed ? 1 : 0);
            tasksCountPerDay[date] = (tasksCountPerDay[date] || 0) + 1;
        });
        let progressDates = Object.keys(tasksCountPerDay).sort((a, b) => new Date(a) - new Date(b));
        let progressValues = progressDates.map(date => Math.round((progressPerDay[date] / tasksCountPerDay[date]) * 100));
        chartLine.data.labels = progressDates;
        chartLine.data.datasets[0].data = progressValues;
        chartLine.update();

        // Gráfico Title: Distribución de la Longitud de los Títulos
        // Definimos bins: <10, 10-20, 20-30, 30-40 y 40+
        let bins = [0, 0, 0, 0, 0];
        data.forEach(task => {
            const length = task.title ? task.title.length : 0;
            if (length < 10) bins[0]++;
            else if (length < 20) bins[1]++;
            else if (length < 30) bins[2]++;
            else if (length < 40) bins[3]++;
            else bins[4]++;
        });
        chartTitle.data.datasets[0].data = bins;
        chartTitle.update();
    } catch (error) {
        console.error("Error actualizando gráficos:", error);
    }
}

// Asignar el evento de actualización al botón
document.getElementById("actualizarDatos").addEventListener("click", actualizarDatosYGraficos);

// Actualizar los gráficos al cargar la página
actualizarDatosYGraficos();