// SmartIntern Custom JavaScript

// Page Loader
document.addEventListener('DOMContentLoaded', function() {
    // Hide loader after page loads
    setTimeout(() => {
        const loader = document.querySelector('.page-loader');
        if (loader) {
            loader.classList.add('fade-out');
            setTimeout(() => loader.remove(), 500);
        }
    }, 500);
});

// Scroll to Top Button
const scrollTopBtn = document.createElement('button');
scrollTopBtn.id = 'scrollTopBtn';
scrollTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
scrollTopBtn.setAttribute('title', 'Scroll to top');
document.body.appendChild(scrollTopBtn);

window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
        scrollTopBtn.style.display = 'flex';
    } else {
        scrollTopBtn.style.display = 'none';
    }
});

scrollTopBtn.addEventListener('click', function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// Auto-dismiss alerts after 5 seconds
document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
});

// Form Validation Enhancement
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.classList.add('was-validated');
    });
});

// File Upload Drag & Drop
document.querySelectorAll('input[type="file"]').forEach(fileInput => {
    const wrapper = fileInput.closest('.mb-3') || fileInput.parentElement;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        wrapper.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        wrapper.addEventListener(eventName, () => {
            wrapper.classList.add('drag-over', 'file-upload-wrapper');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        wrapper.addEventListener(eventName, () => {
            wrapper.classList.remove('drag-over');
        });
    });
    
    wrapper.addEventListener('drop', function(e) {
        const files = e.dataTransfer.files;
        fileInput.files = files;
        
        // Show file name
        if (files.length > 0) {
            const fileLabel = wrapper.querySelector('label') || wrapper;
            const fileName = document.createElement('div');
            fileName.className = 'mt-2 text-success';
            fileName.innerHTML = `<i class="bi bi-check-circle"></i> ${files[0].name}`;
            fileLabel.appendChild(fileName);
        }
    });
});

// Animated Counter for Statistics
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Trigger counter animation when element is in viewport
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.hasAttribute('data-animated')) {
            animateCounter(entry.target);
            entry.target.setAttribute('data-animated', 'true');
        }
    });
});

document.querySelectorAll('.counter').forEach(counter => {
    observer.observe(counter);
});

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast-notification alert alert-${type} alert-dismissible fade show`;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Confirm before delete/reject actions
document.querySelectorAll('[data-confirm]').forEach(element => {
    element.addEventListener('click', function(e) {
        const message = this.getAttribute('data-confirm') || 'Are you sure?';
        if (!confirm(message)) {
            e.preventDefault();
        }
    });
});

// Table Search Functionality
function addTableSearch(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Search table...';
    table.parentElement.insertBefore(searchInput, table);
    
    searchInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

// Progress Bar Animation
document.querySelectorAll('.progress-bar').forEach(bar => {
    const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
    bar.style.width = '0';
    setTimeout(() => {
        bar.style.width = width;
    }, 100);
});

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        showToast('Failed to copy!', 'danger');
    });
}

// Add tooltips to all elements with title attribute
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Add popovers
document.addEventListener('DOMContentLoaded', function() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.forEach(function (popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });
});

// Lazy Loading Images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img.lazy').forEach(img => imageObserver.observe(img));
}

// Form Auto-save (for drafts)
function setupAutosave(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Load saved data
    const saved = localStorage.getItem(storageKey);
    if (saved) {
        const data = JSON.parse(saved);
        Object.keys(data).forEach(name => {
            const field = form.elements[name];
            if (field) field.value = data[name];
        });
    }
    
    // Auto-save on input
    form.addEventListener('input', function() {
        const data = {};
        Array.from(form.elements).forEach(field => {
            if (field.name) data[field.name] = field.value;
        });
        localStorage.setItem(storageKey, JSON.stringify(data));
    });
    
    // Clear on submit
    form.addEventListener('submit', function() {
        localStorage.removeItem(storageKey);
    });
}

// Dark Mode Toggle (Optional)
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

// Keyboard Shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+K or Cmd+K: Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const search = document.querySelector('input[type="search"]');
        if (search) search.focus();
    }
    
    // Escape: Close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.show').forEach(modal => {
            bootstrap.Modal.getInstance(modal).hide();
        });
    }
});

// Print Page
function printPage() {
    window.print();
}

// Export Table to CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tr'));
    const csv = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('th, td'));
        return cells.map(cell => `"${cell.textContent.trim()}"`).join(',');
    }).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

console.log('SmartIntern Custom JS Loaded ✓');
