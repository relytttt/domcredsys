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
    
    // Create and add claim form with proper labels
    const formHtml = `
        <div class="claim-form">
            <div class="form-field">
                <label for="customer-name-${code}" class="claim-form-label">Customer Name *</label>
                <input type="text" id="customer-name-${code}" placeholder="Enter customer name" required autocomplete="name" aria-required="true">
                <span class="error-message" id="name-error-${code}" style="display:none; color:#ef4444; font-size:12px; margin-top:4px;"></span>
            </div>
            <div class="form-field">
                <label for="customer-phone-${code}" class="claim-form-label">Customer Phone Number *</label>
                <input type="tel" id="customer-phone-${code}" placeholder="e.g., 555-1234 or (555) 123-4567" required autocomplete="tel" aria-required="true">
                <span class="error-message" id="phone-error-${code}" style="display:none; color:#ef4444; font-size:12px; margin-top:4px;"></span>
            </div>
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
    const nameError = document.getElementById(`name-error-${code}`);
    const phoneError = document.getElementById(`phone-error-${code}`);
    
    // Clear previous errors
    nameError.style.display = 'none';
    phoneError.style.display = 'none';
    nameError.textContent = '';
    phoneError.textContent = '';
    
    let hasError = false;
    
    // Validate customer name
    if (!customerName) {
        nameError.textContent = 'Please enter customer name';
        nameError.style.display = 'block';
        document.getElementById(`customer-name-${code}`).focus();
        hasError = true;
    } else if (customerName.length < 2) {
        nameError.textContent = 'Name must be at least 2 characters';
        nameError.style.display = 'block';
        document.getElementById(`customer-name-${code}`).focus();
        hasError = true;
    }
    
    // Validate customer phone
    if (!customerPhone) {
        phoneError.textContent = 'Please enter customer phone number';
        phoneError.style.display = 'block';
        if (!hasError) {
            document.getElementById(`customer-phone-${code}`).focus();
        }
        hasError = true;
    } else {
        // Basic phone validation - allow various formats
        const phoneRegex = /^[\d\s\-\(\)\+\.]+$/;
        const digitsOnly = customerPhone.replace(/\D/g, '');
        
        if (!phoneRegex.test(customerPhone)) {
            phoneError.textContent = 'Please enter a valid phone number';
            phoneError.style.display = 'block';
            if (!hasError) {
                document.getElementById(`customer-phone-${code}`).focus();
            }
            hasError = true;
        } else if (digitsOnly.length < 7) {
            phoneError.textContent = 'Phone number must have at least 7 digits';
            phoneError.style.display = 'block';
            if (!hasError) {
                document.getElementById(`customer-phone-${code}`).focus();
            }
            hasError = true;
        }
    }
    
    if (hasError) {
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
