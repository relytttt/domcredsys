// Theme Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Attach theme toggle event listener
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Initialize filter state
    let currentFilter = 'all';
    
    // Attach filter toggle event listeners
    document.querySelectorAll('.filter-toggle-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Update active state
            document.querySelectorAll('.filter-toggle-btn').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Update filter and apply
            currentFilter = this.dataset.filter;
            filterCredits();
        });
    });
    
    // Attach search event listener
    const searchInput = document.getElementById('credit-search');
    if (searchInput) {
        searchInput.addEventListener('input', filterCredits);
    }
    
    // Add swipe gesture support for filter toggle
    let touchStartX = 0;
    let touchEndX = 0;
    const creditsGrid = document.querySelector('.credits-grid');
    
    if (creditsGrid) {
        creditsGrid.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        creditsGrid.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipeGesture();
        }, { passive: true });
    }
    
    function handleSwipeGesture() {
        const swipeThreshold = 100; // Minimum distance for swipe
        const swipeDistance = touchEndX - touchStartX;
        
        if (Math.abs(swipeDistance) > swipeThreshold) {
            const filterButtons = Array.from(document.querySelectorAll('.filter-toggle-btn'));
            const currentIndex = filterButtons.findIndex(btn => btn.classList.contains('active'));
            
            if (swipeDistance > 0) {
                // Swipe right - go to previous filter
                if (currentIndex > 0) {
                    filterButtons[currentIndex - 1].click();
                }
            } else {
                // Swipe left - go to next filter
                if (currentIndex < filterButtons.length - 1) {
                    filterButtons[currentIndex + 1].click();
                }
            }
        }
    }
    
    // Modified filterCredits function to respect current filter
    function filterCredits() {
        const query = (document.getElementById('credit-search')?.value || '').toLowerCase().trim();
        const tiles = document.querySelectorAll('.credit-tile');
        const noResults = document.getElementById('no-results');
        let visibleCount = 0;
        
        tiles.forEach(tile => {
            const code = tile.dataset.code.toLowerCase();
            const customerPhone = (tile.dataset.customerPhone || '').toLowerCase();
            const customerName = (tile.dataset.customerName || '').toLowerCase();
            const status = tile.dataset.status;
            
            // Check if matches search query
            const matchesSearch = !query || code.includes(query) || customerPhone.includes(query) || customerName.includes(query);
            
            // Check if matches current filter
            const matchesFilter = currentFilter === 'all' || status === currentFilter;
            
            // Show tile only if it matches both search and filter
            if (matchesSearch && matchesFilter) {
                tile.style.display = 'flex';
                visibleCount++;
            } else {
                tile.style.display = 'none';
            }
        });
        
        // Show/hide no results message
        if (noResults) {
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }
    
    // Attach claim button event listeners
    document.querySelectorAll('.btn-claim').forEach(button => {
        button.addEventListener('click', function() {
            const tile = this.closest('.credit-tile');
            const code = tile.dataset.code;
            const customerName = tile.dataset.customerName || 'this customer';
            if (confirm(`Claim credit ${code} for ${customerName}?`)) {
                submitClaim(code);
            }
        });
    });
    
    // Attach unclaim button event listeners
    document.querySelectorAll('.btn-unclaim').forEach(button => {
        button.addEventListener('click', function() {
            const tile = this.closest('.credit-tile');
            const code = tile.dataset.code;
            if (confirm(`Are you sure you want to unclaim credit ${code}?`)) {
                submitUnclaim(code);
            }
        });
    });
    
    // Attach item input Enter key listener
    const itemInput = document.getElementById('item-input');
    if (itemInput) {
        itemInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addItem();
            }
        });
    }
    
    // Form submit validation
    const createCreditForm = document.getElementById('create-credit-form');
    if (createCreditForm) {
        createCreditForm.addEventListener('submit', function(e) {
            if (items.length === 0) {
                e.preventDefault();
                alert('Please add at least one item');
                return false;
            }
        });
    }
});

// Items management for the add item tag system
let items = [];

function addItem() {
    const input = document.getElementById('item-input');
    const value = input.value.trim();
    if (value && !items.includes(value)) {
        items.push(value);
        renderItems();
        input.value = '';
    }
    input.focus();
}

function removeItem(index) {
    items.splice(index, 1);
    renderItems();
}

function renderItems() {
    const container = document.getElementById('items-tags');
    const hidden = document.getElementById('items-hidden');
    
    if (!container || !hidden) return;
    
    container.innerHTML = items.map((item, i) => 
        `<span class="item-tag">${escapeHtml(item)} <button type="button" onclick="removeItem(${i})">×</button></span>`
    ).join('');
    
    hidden.value = JSON.stringify(items);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
    }
}

// Submit Claim - uses customer details stored at credit creation
function submitClaim(code) {
    // Get claim URL from data attribute
    const creditsGrid = document.querySelector('.credits-grid');
    const claimUrl = creditsGrid ? creditsGrid.dataset.claimUrl : '/claim-credit';
    
    // Create a form and submit it
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = claimUrl;
    
    const codeInput = document.createElement('input');
    codeInput.type = 'hidden';
    codeInput.name = 'code';
    codeInput.value = code;
    
    form.appendChild(codeInput);
    document.body.appendChild(form);
    form.submit();
}

function submitUnclaim(code) {
    // Get unclaim URL from data attribute
    const creditsGrid = document.querySelector('.credits-grid');
    const unclaimUrl = creditsGrid ? creditsGrid.dataset.unclaimUrl : '/unclaim-credit';
    
    // Create a form and submit it
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = unclaimUrl;
    
    const codeInput = document.createElement('input');
    codeInput.type = 'hidden';
    codeInput.name = 'code';
    codeInput.value = code;
    
    form.appendChild(codeInput);
    document.body.appendChild(form);
    form.submit();
}
