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
    
    // Attach search event listener
    const searchInput = document.getElementById('credit-search');
    if (searchInput) {
        searchInput.addEventListener('input', filterCredits);
    }
    
    // Attach claim button event listeners
    document.querySelectorAll('.btn-claim').forEach(button => {
        button.addEventListener('click', function() {
            const tile = this.closest('.credit-tile');
            const code = tile.dataset.code;
            // Directly submit claim without showing form
            submitClaim(code);
        });
    });
    
    // Attach unclaim button event listeners
    document.querySelectorAll('.btn-unclaim').forEach(button => {
        button.addEventListener('click', function() {
            const tile = this.closest('.credit-tile');
            const code = tile.dataset.code;
            if (confirm('Are you sure you want to unclaim this credit?')) {
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

// Search/Filter Functionality for Credits
function filterCredits() {
    const query = document.getElementById('credit-search').value.toLowerCase().trim();
    const tiles = document.querySelectorAll('.credit-tile');
    const noResults = document.getElementById('no-results');
    let visibleCount = 0;
    
    tiles.forEach(tile => {
        const code = tile.dataset.code.toLowerCase();
        const claimedBy = (tile.dataset.claimedBy || '').toLowerCase();
        
        if (code.includes(query) || claimedBy.includes(query)) {
            tile.style.display = 'flex';
            visibleCount++;
        } else {
            tile.style.display = 'none';
        }
    });
    
    // Show/hide no results message
    if (noResults) {
        noResults.style.display = visibleCount === 0 && query !== '' ? 'block' : 'none';
    }
}

// Claim Form Handling
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
