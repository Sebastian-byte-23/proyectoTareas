const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const openModalBtn = document.getElementById('openModalBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const modal = document.getElementById('taskModal');

// Búsqueda interactiva
searchInput.addEventListener('input', async (event) => {
    const query = event.target.value;

    if (!query) {
        searchResults.classList.add('hidden');
        searchResults.innerHTML = '';
        return;
    }

    const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
    const data = await response.json();

    if (data.results && data.results.length > 0) {
        searchResults.classList.remove('hidden');
        searchResults.innerHTML = data.results.map(result => `
            <div class="p-2 hover:bg-blue-100 cursor-pointer">
                <a href="/task/${result.id}" class="block text-gray-800" onclick="return validateTask(${result.id});">
                    ${result.title}
                </a>
            </div>
        `).join('');
    } else {
        searchResults.classList.remove('hidden');
        searchResults.innerHTML = '<div class="p-2 text-gray-500">No se encontraron resultados</div>';
    }
});

// Validación de tareas
async function validateTask(taskId) {
    const response = await fetch(`/task/${taskId}`);
    if (response.status === 404) {
        alert("La tarea seleccionada ya no está disponible.");
        return false;
    }
    return true;
}

// Modal
openModalBtn.addEventListener('click', () => modal.classList.remove('hidden'));
closeModalBtn.addEventListener('click', () => modal.classList.add('hidden'));
window.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.add('hidden');
});
