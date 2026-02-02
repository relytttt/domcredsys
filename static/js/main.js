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
            showClaimForm(tile, code);
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

// Search/Filter Functionality for Credits
function filterCredits() {
    const query = document.getElementById('credit-search').value.toLowerCase().trim();
    const tiles = document.querySelectorAll('.credit-tile');
    const noResults = document.getElementById('no-results');
    let visibleCount = 0;
    
    tiles.forEach(tile => {
        const code = tile.dataset.code.toLowerCase();
        const customerPhone = (tile.dataset.customerPhone || '').toLowerCase();
        
        if (code.includes(query) || customerPhone.includes(query)) {
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

// Show Claim Form
function showClaimForm(tile, code) {
    // Check if form already exists
    if (tile.querySelector('.claim-form')) {
        return;
    }
    
    // Hide the claim button
    const footer = tile.querySelector('.tile-footer');
    footer.style.display = 'none';
    
    // Create and add claim form
    const formHtml = `
        <div class="claim-form">
            <input type="text" id="customer-name-${code}" placeholder="Customer Name *" required autocomplete="name">
            <input type="tel" id="customer-phone-${code}" placeholder="Customer Phone Number *" required autocomplete="tel">
            <div class="claim-form-buttons">
                <button type="button" class="btn-submit" onclick="submitClaimWithDetails('${code}')">Submit Claim</button>
                <button type="button" class="btn-cancel" onclick="hideClaimForm('${code}')">Cancel</button>
            </div>
        </div>
    `;
    
    tile.insertAdjacentHTML('beforeend', formHtml);
    
    // Focus on customer name input
    document.getElementById(`customer-name-${code}`).focus();
}

// Hide Claim Form
function hideClaimForm(code) {
    const tiles = document.querySelectorAll('.credit-tile');
    tiles.forEach(tile => {
        if (tile.dataset.code === code) {
            const form = tile.querySelector('.claim-form');
            if (form) {
                form.remove();
            }
            const footer = tile.querySelector('.tile-footer');
            if (footer) {
                footer.style.display = 'block';
            }
        }
    });
}

// Submit Claim with Customer Details
function submitClaimWithDetails(code) {
    const customerName = document.getElementById(`customer-name-${code}`).value.trim();
    const customerPhone = document.getElementById(`customer-phone-${code}`).value.trim();
    
    // Validate inputs
    if (!customerName) {
        alert('Please enter customer name');
        document.getElementById(`customer-name-${code}`).focus();
        return;
    }
    
    if (!customerPhone) {
        alert('Please enter customer phone number');
        document.getElementById(`customer-phone-${code}`).focus();
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
    
    const phoneInput = document.createElement('input');
    phoneInput.type = 'hidden';
    phoneInput.name = 'customer_phone';
    phoneInput.value = customerPhone;
    
    form.appendChild(codeInput);
    form.appendChild(nameInput);
    form.appendChild(phoneInput);
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
