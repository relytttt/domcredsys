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
            showClaimForm(code);
        });
    });
    
    // Attach cancel button event listeners
    document.querySelectorAll('.btn-cancel').forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('.claim-form');
            const code = form.id.replace('claim-form-', '');
            hideClaimForm(code);
        });
    });
    
    // Attach submit button event listeners
    document.querySelectorAll('.btn-submit').forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('.claim-form');
            const code = form.id.replace('claim-form-', '');
            submitClaim(code);
        });
    });
});

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
function showClaimForm(code) {
    const form = document.getElementById('claim-form-' + code);
    if (form) {
        form.style.display = 'flex';
        // Focus on input
        const input = document.getElementById('claim-input-' + code);
        if (input) {
            input.focus();
        }
    }
}

function hideClaimForm(code) {
    const form = document.getElementById('claim-form-' + code);
    if (form) {
        form.style.display = 'none';
        // Clear input
        const input = document.getElementById('claim-input-' + code);
        if (input) {
            input.value = '';
        }
    }
}

function submitClaim(code) {
    const input = document.getElementById('claim-input-' + code);
    const customerName = input ? input.value.trim() : '';
    
    if (!customerName) {
        alert('Please enter customer name/phone number');
        return;
    }
    
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
    
    const nameInput = document.createElement('input');
    nameInput.type = 'hidden';
    nameInput.name = 'customer_name';
    nameInput.value = customerName;
    
    form.appendChild(codeInput);
    form.appendChild(nameInput);
    document.body.appendChild(form);
    form.submit();
}
