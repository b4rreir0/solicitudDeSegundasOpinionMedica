// JavaScript principal para el Sistema de Solicitud de Segundas Opiniones Médicas

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers de Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts después de 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Configurar área de drag and drop para archivos
    setupFileUpload();

    // Configurar formularios con validación
    setupFormValidation();

    // Configurar búsqueda en tiempo real
    setupLiveSearch();

    // Configurar confirmaciones de eliminación
    setupDeleteConfirmations();
});

// Función para configurar el área de subida de archivos
function setupFileUpload() {
    const fileUploadArea = document.querySelector('.file-upload-area');
    const fileInput = document.querySelector('#file-input');

    if (fileUploadArea && fileInput) {
        fileUploadArea.addEventListener('click', function() {
            fileInput.click();
        });

        fileUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            fileUploadArea.classList.add('drag-over');
        });

        fileUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            fileUploadArea.classList.remove('drag-over');
        });

        fileUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            fileUploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelection(files);
            }
        });

        fileInput.addEventListener('change', function(e) {
            handleFileSelection(e.target.files);
        });
    }
}

// Función para manejar la selección de archivos
function handleFileSelection(files) {
    const fileList = document.querySelector('#file-list');
    if (fileList) {
        fileList.innerHTML = '';
        
        Array.from(files).forEach(function(file) {
            const fileItem = document.createElement('div');
            fileItem.className = 'alert alert-info d-flex justify-content-between align-items-center';
            fileItem.innerHTML = `
                <div>
                    <i class="fas fa-file me-2"></i>
                    <strong>${file.name}</strong>
                    <small class="text-muted ms-2">(${formatFileSize(file.size)})</small>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(this)">
                    <i class="fas fa-times"></i>
                </button>
            `;
            fileList.appendChild(fileItem);
        });
    }
}

// Función para formatear el tamaño de archivo
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Función para remover archivo de la lista
function removeFile(button) {
    button.closest('.alert').remove();
}

// Función para configurar validación de formularios
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Función para configurar búsqueda en tiempo real
function setupLiveSearch() {
    const searchInput = document.querySelector('#search-input');
    const searchResults = document.querySelector('#search-results');
    
    if (searchInput && searchResults) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(function() {
                    performSearch(query);
                }, 300);
            } else {
                searchResults.innerHTML = '';
            }
        });
    }
}

// Función para realizar búsqueda
function performSearch(query) {
    const searchResults = document.querySelector('#search-results');
    searchResults.innerHTML = '<div class="text-center"><div class="loading-spinner"></div></div>';
    
    // Simular llamada AJAX
    setTimeout(function() {
        searchResults.innerHTML = `
            <div class="list-group">
                <div class="list-group-item">
                    <h6 class="mb-1">Resultado de ejemplo</h6>
                    <p class="mb-1">Descripción del resultado para: ${query}</p>
                    <small class="text-muted">Hace 3 días</small>
                </div>
            </div>
        `;
    }, 500);
}

// Función para configurar confirmaciones de eliminación
function setupDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemName = this.dataset.itemName || 'este elemento';
            
            if (confirm(`¿Estás seguro de que deseas eliminar ${itemName}? Esta acción no se puede deshacer.`)) {
                // Proceder con la eliminación
                const form = this.closest('form');
                if (form) {
                    form.submit();
                } else {
                    window.location.href = this.href;
                }
            }
        });
    });
}

// Función para mostrar notificaciones toast
function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('#toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remover el toast después de que se oculte
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Función para crear el contenedor de toasts
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Función para copiar texto al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copiado al portapapeles', 'success');
    }, function(err) {
        showToast('Error al copiar', 'danger');
    });
}

// Función para confirmar acción
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Función para mostrar modal de carga
function showLoadingModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'loading-modal';
    modal.innerHTML = `
        <div class="modal-dialog modal-sm modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-body text-center">
                    <div class="loading-spinner mx-auto mb-3"></div>
                    <p class="mb-0">Procesando...</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    return bsModal;
}

// Función para ocultar modal de carga
function hideLoadingModal(modal) {
    modal.hide();
    setTimeout(function() {
        document.querySelector('#loading-modal').remove();
    }, 300);
}

// Función para actualizar badge de notificaciones
function updateNotificationBadge(count) {
    const badge = document.querySelector('#notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    }
}

// Funciones para manejo de fechas
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función para el tiempo relativo
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
        return `hace ${days} día${days > 1 ? 's' : ''}`;
    } else if (hours > 0) {
        return `hace ${hours} hora${hours > 1 ? 's' : ''}`;
    } else if (minutes > 0) {
        return `hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    } else {
        return 'hace un momento';
    }
}

// Exportar funciones para uso global
window.showToast = showToast;
window.copyToClipboard = copyToClipboard;
window.confirmAction = confirmAction;
window.showLoadingModal = showLoadingModal;
window.hideLoadingModal = hideLoadingModal;
window.updateNotificationBadge = updateNotificationBadge;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.timeAgo = timeAgo;
