// Gestion des tâches côté client
document.addEventListener('DOMContentLoaded', function() {
    loadTasks();
    setupEventListeners();
});

function setupEventListeners() {
    // Formulaire de tâche
    document.getElementById('taskForm').addEventListener('submit', handleTaskSubmit);
    
    // Filtres
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const status = this.getAttribute('data-status');
            loadTasks(status);
            
            // Mettre à jour l'état actif des boutons
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

async function loadTasks(status = '') {
    try {
        const url = status ? `/api/tasks?status=${status}` : '/api/tasks';
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Erreur lors du chargement des tâches');
        }
        
        const tasks = await response.json();
        displayTasks(tasks);
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement des tâches', 'danger');
    }
}

function displayTasks(tasks) {
    const container = document.getElementById('tasks-container');
    
    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle"></i> Aucune tâche trouvée.
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = tasks.map(task => `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card task-card priority-${task.priority} h-100">
                <div class="card-body">
                    <h5 class="card-title">${escapeHtml(task.title)}</h5>
                    <p class="card-text">${escapeHtml(task.description || 'Aucune description')}</p>
                    
                    <div class="mb-2">
                        <span class="badge bg-${getStatusBadgeColor(task.status)}">${getStatusText(task.status)}</span>
                        <span class="badge bg-secondary">Priorité ${task.priority}</span>
                    </div>
                    
                    ${task.due_date ? `
                        <div class="mb-2">
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> Échéance: ${new Date(task.due_date).toLocaleDateString()}
                            </small>
                        </div>
                    ` : ''}
                </div>
                <div class="card-footer bg-transparent">
                    <div class="btn-group btn-group-sm w-100">
                        <button class="btn btn-outline-primary" onclick="editTask(${task.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="toggleTaskStatus(${task.id}, '${task.status}')">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="deleteTask(${task.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function getStatusBadgeColor(status) {
    const colors = {
        'pending': 'warning',
        'in_progress': 'info',
        'completed': 'success'
    };
    return colors[status] || 'secondary';
}

function getStatusText(status) {
    const texts = {
        'pending': 'En attente',
        'in_progress': 'En cours',
        'completed': 'Terminée'
    };
    return texts[status] || status;
}

async function handleTaskSubmit(event) {
    event.preventDefault();
    
    const formData = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        priority: parseInt(document.getElementById('priority').value),
        due_date: document.getElementById('due_date').value || null
    };
    
    const taskId = document.getElementById('taskId').value;
    const url = taskId ? `/api/tasks/${taskId}` : '/api/tasks';
    const method = taskId ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la sauvegarde');
        }
        
        // Fermer le modal et recharger les tâches
        const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
        modal.hide();
        
        resetForm();
        loadTasks();
        
        showAlert('Tâche sauvegardée avec succès!', 'success');
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la sauvegarde de la tâche', 'danger');
    }
}

async function editTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`);
        if (!response.ok) throw new Error('Tâche non trouvée');
        
        const task = await response.json();
        
        // Remplir le formulaire
        document.getElementById('taskId').value = task.id;
        document.getElementById('title').value = task.title;
        document.getElementById('description').value = task.description || '';
        document.getElementById('priority').value = task.priority;
        
        if (task.due_date) {
            const dueDate = new Date(task.due_date);
            document.getElementById('due_date').value = dueDate.toISOString().slice(0, 16);
        } else {
            document.getElementById('due_date').value = '';
        }
        
        document.getElementById('modalTitle').textContent = 'Modifier la tâche';
        
        // Ouvrir le modal
        const modal = new bootstrap.Modal(document.getElementById('taskModal'));
        modal.show();
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement de la tâche', 'danger');
    }
}

async function toggleTaskStatus(taskId, currentStatus) {
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!response.ok) throw new Error('Erreur lors de la mise à jour');
        
        loadTasks();
        showAlert('Statut de la tâche mis à jour!', 'success');
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la mise à jour de la tâche', 'danger');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette tâche ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Erreur lors de la suppression');
        
        loadTasks();
        showAlert('Tâche supprimée avec succès!', 'success');
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la suppression de la tâche', 'danger');
    }
}

function resetForm() {
    document.getElementById('taskForm').reset();
    document.getElementById('taskId').value = '';
    document.getElementById('modalTitle').textContent = 'Nouvelle Tâche';
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    // Auto-supprimer après 5 secondes
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}