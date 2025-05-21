// Common JavaScript functions for the entire application

// Reszponzív viselkedés kezelése
function handleResponsiveLayout() {
    const isMobile = window.innerWidth <= 480;
    const isTablet = window.innerWidth <= 768;
    
    // Táblázatok görgetése
    document.querySelectorAll('.table-container').forEach(container => {
        container.style.maxHeight = isMobile ? '300px' : 'none';
    });

    // Gombok elrendezése
    document.querySelectorAll('.button-group').forEach(group => {
        group.style.flexDirection = isMobile ? 'column' : 'row';
        group.style.gap = isMobile ? '0.5rem' : '1rem';
    });

    // Modal méret és pozíció
    document.querySelectorAll('.modal').forEach(modal => {
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.width = isMobile ? '95vw' : 'min(500px, 95vw)';
            modalContent.style.padding = isMobile ? '1rem' : '2rem';
        }
    });

    // Grid elrendezés
    document.querySelectorAll('.grid').forEach(grid => {
        if (isMobile) {
            grid.style.gridTemplateColumns = '1fr';
        } else if (isTablet) {
            if (grid.classList.contains('grid-4')) {
                grid.style.gridTemplateColumns = 'repeat(2, 1fr)';
            } else if (grid.classList.contains('grid-3')) {
                grid.style.gridTemplateColumns = 'repeat(2, 1fr)';
            }
        }
    });
}

// Eseménykezelők hozzáadása
window.addEventListener('resize', handleResponsiveLayout);
window.addEventListener('load', handleResponsiveLayout);

// Header scroll effect
function handleHeaderScroll() {
    const header = document.querySelector('.header');
    if (window.scrollY > 0) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
}

window.addEventListener('scroll', throttle(handleHeaderScroll, 100));
window.addEventListener('load', handleHeaderScroll);

// Üzenetek megjelenítése
function showMessage(message, type = 'info') {
    const flashContainer = document.querySelector('.flash-messages') || createFlashContainer();
    const messageDiv = document.createElement('div');
    messageDiv.className = `flash-message ${type}`;
    
    // Message content
    const messageContent = document.createElement('div');
    messageContent.className = 'flash-content';
    messageContent.textContent = message;
    messageDiv.appendChild(messageContent);
    
    // Progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'flash-progress';
    messageDiv.appendChild(progressBar);
    
    flashContainer.appendChild(messageDiv);

    // Üzenet eltüntetése
    const duration = type === 'error' ? 5000 : 3000;
    
    setTimeout(() => {
        messageDiv.classList.add('fade-out');
        setTimeout(() => {
            messageDiv.remove();
            if (flashContainer.children.length === 0) {
                flashContainer.remove();
            }
        }, 500);
    }, duration);
}

function showSuccess(message) {
    showMessage(message, 'success');
}

function showError(message) {
    showMessage(message, 'error');
}

function showWarning(message) {
    showMessage(message, 'warning');
}

function showInfo(message) {
    showMessage(message, 'info');
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

// Modal kezelés
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        // Első input mező fókuszba állítása
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            firstInput.focus();
        }
        // ESC gomb kezelése
        document.addEventListener('keydown', handleEscKey);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        // Form reset
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
        // ESC gomb kezelés eltávolítása
        document.removeEventListener('keydown', handleEscKey);
    }
}

function handleEscKey(event) {
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal[style*="display: flex"]');
        if (openModal) {
            closeModal(openModal.id);
        }
    }
}

// Modal bezárása kattintásra a háttéren
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
});

// Form validáció
function validateForm(form) {
    const requiredInputs = form.querySelectorAll('[required]');
    let isValid = true;
    let firstInvalidInput = null;

    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('invalid');
            if (!firstInvalidInput) {
                firstInvalidInput = input;
            }
        } else {
            input.classList.remove('invalid');
        }
    });

    if (!isValid && firstInvalidInput) {
        firstInvalidInput.focus();
        showError('Kérjük, töltse ki az összes kötelező mezőt!');
    }

    return isValid;
}

// Form submit eseménykezelő hozzáadása
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(event) {
        if (!validateForm(this)) {
            event.preventDefault();
        }
    });
});

// Input mezők validációja
document.querySelectorAll('input, select, textarea').forEach(input => {
    input.addEventListener('input', function() {
        if (this.hasAttribute('required')) {
            if (this.value.trim()) {
                this.classList.remove('invalid');
            } else {
                this.classList.add('invalid');
            }
        }
    });
});

// Táblázat rendezés
function sortTable(table, column, type = 'string') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelector('th:nth-child(' + (column + 1) + ')');
    const isAsc = header.classList.contains('asc');
    
    // Rendezési irány váltása
    table.querySelectorAll('th').forEach(th => th.classList.remove('asc', 'desc'));
    header.classList.add(isAsc ? 'desc' : 'asc');

    // Rendezés
    rows.sort((a, b) => {
        let aVal = a.cells[column].textContent.trim();
        let bVal = b.cells[column].textContent.trim();

        if (type === 'number') {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
        } else if (type === 'date') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        }

        if (aVal < bVal) return isAsc ? 1 : -1;
        if (aVal > bVal) return isAsc ? -1 : 1;
        return 0;
    });

    // Táblázat frissítése
    rows.forEach(row => tbody.appendChild(row));
}

// Táblázat keresés
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    searchTerm = searchTerm.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// Táblázat exportálás
function exportTableToCSV(table, filename) {
    const rows = table.querySelectorAll('tr');
    const csv = [];
    
    for (const row of rows) {
        const cells = row.querySelectorAll('th, td');
        const rowData = Array.from(cells).map(cell => {
            let text = cell.textContent.trim();
            // CSV formátumhoz escape
            if (text.includes(',') || text.includes('"') || text.includes('\n')) {
                text = '"' + text.replace(/"/g, '""') + '"';
            }
            return text;
        });
        csv.push(rowData.join(','));
    }
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (navigator.msSaveBlob) {
        // IE 10+
        navigator.msSaveBlob(blob, filename);
    } else {
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Táblázat nyomtatás
function printTable(table) {
    const printWindow = window.open('', '_blank');
    const tableClone = table.cloneNode(true);
    
    // Nyomtatási stílusok
    printWindow.document.write(`
        <html>
            <head>
                <title>Táblázat nyomtatása</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f5f5f5; }
                    @media print {
                        body { margin: 0; padding: 15px; }
                        table { page-break-inside: auto; }
                        tr { page-break-inside: avoid; page-break-after: auto; }
                    }
                </style>
            </head>
            <body>
                ${tableClone.outerHTML}
            </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
    printWindow.close();
}

// Fájl feltöltés előnézet
function previewFile(input, previewElement) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        if (file.type.startsWith('image/')) {
            previewElement.innerHTML = `<img src="${e.target.result}" alt="Előnézet" style="max-width: 100%; max-height: 200px;">`;
        } else {
            previewElement.textContent = `Fájl: ${file.name} (${formatFileSize(file.size)})`;
        }
    };
    reader.readAsDataURL(file);
}

// Fájl méret formázása
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Dátum formázás
function formatDate(date, format = 'hu-HU') {
    return new Date(date).toLocaleDateString(format, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Szám formázás
function formatNumber(number, locale = 'hu-HU') {
    return new Intl.NumberFormat(locale).format(number);
}

// Betöltés indikátor
function showLoading() {
    const loader = document.createElement('div');
    loader.className = 'loading-overlay';
    loader.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <div class="loading-text">Betöltés...</div>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.querySelector('.loading-overlay');
    if (loader) {
        loader.remove();
    }
}

// AJAX kérés
async function fetchData(url, options = {}) {
    showLoading();
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Hiba:', error);
        showError('Hiba történt a kérés feldolgozása közben');
        throw error;
    } finally {
        hideLoading();
    }
}

// Debounce függvény
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle függvény
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Reszponzív kép kezelés
function handleResponsiveImages() {
    document.querySelectorAll('img[data-src]').forEach(img => {
        const src = img.getAttribute('data-src');
        if (window.innerWidth <= 480) {
            img.src = src.replace('.jpg', '-small.jpg');
        } else if (window.innerWidth <= 768) {
            img.src = src.replace('.jpg', '-medium.jpg');
        } else {
            img.src = src;
        }
    });
}

// Lazy loading
function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));
}

// Accessibility
function initAccessibility() {
    // ARIA attribútumok hozzáadása
    document.querySelectorAll('button:not([aria-label])').forEach(button => {
        if (button.textContent.trim()) {
            button.setAttribute('aria-label', button.textContent.trim());
        }
    });

    // Billentyűzet navigáció
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });

    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });

    // Skip link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link visually-hidden';
    skipLink.textContent = 'Ugrás a tartalomhoz';
    document.body.insertBefore(skipLink, document.body.firstChild);
}

// Inicializálás
document.addEventListener('DOMContentLoaded', function() {
    handleResponsiveLayout();
    handleResponsiveImages();
    initLazyLoading();
    initAccessibility();
}); 