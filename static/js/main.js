// Global variables
let selectedProducts = [];
let uninstallInProgress = false;
let logArea;

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

// Initialize the application
function initApp() {
    // Get DOM elements
    const productCheckboxes = document.querySelectorAll('.product-checkbox');
    const selectAllCheckbox = document.getElementById('select-all');
    const uninstallButton = document.getElementById('uninstall-button');
    const deleteFolderCheckbox = document.getElementById('delete-folder');
    const restartComputerCheckbox = document.getElementById('restart-computer');
    logArea = document.getElementById('log-area');
    
    // Add event listeners
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', handleSelectAll);
    }
    
    if (productCheckboxes) {
        productCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateSelectedProducts);
        });
    }
    
    if (uninstallButton) {
        uninstallButton.addEventListener('click', startUninstallation);
    }
    
    // Initialize tooltips
    initTooltips();
    
    // Initial update of selected products
    updateSelectedProducts();
    
    // Log initial message
    logMessage('Application initialized. Ready to uninstall Autodesk products.', 'info');
}

// Initialize Bootstrap tooltips
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Handle "Select All" checkbox
function handleSelectAll(event) {
    const isChecked = event.target.checked;
    const productCheckboxes = document.querySelectorAll('.product-checkbox');
    
    productCheckboxes.forEach(checkbox => {
        checkbox.checked = isChecked;
    });
    
    updateSelectedProducts();
}

// Update the list of selected products
function updateSelectedProducts() {
    const productCheckboxes = document.querySelectorAll('.product-checkbox:checked');
    const uninstallButton = document.getElementById('uninstall-button');
    const selectedCount = document.getElementById('selected-count');
    
    // Clear the previous selection
    selectedProducts = [];
    
    // Add each checked product to the selection
    productCheckboxes.forEach(checkbox => {
        selectedProducts.push(checkbox.value);
    });
    
    // Update the UI
    if (selectedCount) {
        selectedCount.textContent = selectedProducts.length;
    }
    
    if (uninstallButton) {
        uninstallButton.disabled = selectedProducts.length === 0 || uninstallInProgress;
    }
}

// Start the uninstallation process
function startUninstallation() {
    if (selectedProducts.length === 0) {
        showAlert('Please select at least one product to uninstall.', 'warning');
        return;
    }
    
    // Show confirmation modal
    const confirmModal = new bootstrap.Modal(document.getElementById('confirm-modal'));
    const productList = document.getElementById('confirm-product-list');
    const confirmButton = document.getElementById('confirm-uninstall-button');
    
    // Get product names from checkboxes
    productList.innerHTML = '';
    selectedProducts.forEach(productId => {
        const checkbox = document.querySelector(`.product-checkbox[value="${productId}"]`);
        const productName = checkbox.dataset.name;
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.textContent = productName;
        productList.appendChild(listItem);
    });
    
    // Show the modal
    confirmModal.show();
    
    // Set up confirm button
    confirmButton.onclick = () => {
        confirmModal.hide();
        performUninstallation();
    };
}

// Perform the actual uninstallation
function performUninstallation() {
    // Get options
    const deleteFolder = document.getElementById('delete-folder').checked;
    const restartComputer = document.getElementById('restart-computer').checked;
    
    // Update UI state
    uninstallInProgress = true;
    updateUIForUninstallInProgress(true);
    
    // Log the start of uninstallation
    logMessage('Starting uninstallation process...', 'info');
    logMessage(`Selected ${selectedProducts.length} products for uninstallation`, 'info');
    if (deleteFolder) {
        logMessage('Will delete C:\\Autodesk folder after uninstallation', 'info');
    }
    if (restartComputer) {
        logMessage('Will restart computer after uninstallation', 'warning');
    }
    
    // Show progress indicator
    const progressBar = document.getElementById('uninstall-progress');
    progressBar.style.width = '5%';
    progressBar.classList.remove('d-none');
    
    // Prepare the request data
    const requestData = {
        productIds: selectedProducts,
        deleteFolder: deleteFolder,
        restartComputer: restartComputer
    };
    
    // Send the uninstall request
    fetch('/uninstall', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        progressBar.style.width = '100%';
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Log success message
            logMessage(data.message, 'success');
            
            // Log details about each product's uninstallation
            if (data.results) {
                logUninstallResults(data.results);
            }
            
            // Log folder deletion result
            if (deleteFolder) {
                if (data.folderDeleted) {
                    logMessage('C:\\Autodesk folder was successfully deleted', 'success');
                } else {
                    logMessage('Failed to delete C:\\Autodesk folder', 'warning');
                }
            }
            
            // Show success message
            showAlert(data.message, 'success');
            
            // If restart was requested, show a message
            if (restartComputer) {
                logMessage('System will restart shortly...', 'warning');
                showAlert('System will restart shortly...', 'warning');
            }
            
            // Refresh the product list after uninstallation
            setTimeout(() => {
                if (!restartComputer) {
                    refreshProductList();
                }
            }, 2000);
        } else {
            throw new Error(data.error || 'An unknown error occurred');
        }
    })
    .catch(error => {
        logMessage(`Error: ${error.message}`, 'error');
        showAlert(`Error: ${error.message}`, 'danger');
        progressBar.classList.add('bg-danger');
    })
    .finally(() => {
        if (!restartComputer) {
            uninstallInProgress = false;
            updateUIForUninstallInProgress(false);
        }
    });
}

// Log uninstallation results
function logUninstallResults(results) {
    if (Array.isArray(results)) {
        results.forEach(result => {
            let logType = 'info';
            if (result.status === 'success') {
                logType = 'success';
            } else if (result.status === 'warning') {
                logType = 'warning';
            } else if (result.status === 'error') {
                logType = 'error';
            }
            
            if (result.displayName) {
                logMessage(`${result.displayName}: ${result.message}`, logType);
            } else {
                logMessage(result.message, logType);
            }
        });
    } else if (typeof results === 'object') {
        // Single result object
        let logType = results.status === 'success' ? 'success' : 
                      results.status === 'warning' ? 'warning' : 
                      results.status === 'error' ? 'error' : 'info';
        
        logMessage(results.message, logType);
    }
}

// Update the UI elements when uninstallation is in progress
function updateUIForUninstallInProgress(inProgress) {
    const uninstallButton = document.getElementById('uninstall-button');
    const productCheckboxes = document.querySelectorAll('.product-checkbox');
    const selectAllCheckbox = document.getElementById('select-all');
    const optionsControls = document.querySelectorAll('.options-control');
    const progressArea = document.getElementById('progress-area');
    
    if (inProgress) {
        // Disable UI controls during uninstallation
        if (uninstallButton) {
            uninstallButton.disabled = true;
            uninstallButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uninstalling...';
        }
        
        productCheckboxes.forEach(checkbox => {
            checkbox.disabled = true;
        });
        
        if (selectAllCheckbox) {
            selectAllCheckbox.disabled = true;
        }
        
        optionsControls.forEach(control => {
            control.disabled = true;
        });
        
        if (progressArea) {
            progressArea.classList.remove('d-none');
        }
    } else {
        // Re-enable UI controls after uninstallation
        if (uninstallButton) {
            uninstallButton.disabled = selectedProducts.length === 0;
            uninstallButton.innerHTML = 'Uninstall Selected';
        }
        
        productCheckboxes.forEach(checkbox => {
            checkbox.disabled = false;
        });
        
        if (selectAllCheckbox) {
            selectAllCheckbox.disabled = false;
        }
        
        optionsControls.forEach(control => {
            control.disabled = false;
        });
        
        if (progressArea) {
            setTimeout(() => {
                progressArea.classList.add('d-none');
                const progressBar = document.getElementById('uninstall-progress');
                progressBar.style.width = '0%';
                progressBar.classList.remove('bg-danger');
            }, 2000);
        }
    }
}

// Refresh the product list
function refreshProductList() {
    fetch('/get-products')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Log the refreshed product list
                logMessage('Refreshed product list', 'info');
                
                // If needed, update the UI with the new product list
                const productListElement = document.getElementById('product-list');
                
                if (productListElement && data.products.length > 0) {
                    updateProductListUI(productListElement, data.products);
                } else if (productListElement) {
                    productListElement.innerHTML = '<div class="alert alert-info">No Autodesk products found installed.</div>';
                }
            } else {
                throw new Error(data.error || 'Failed to refresh product list');
            }
        })
        .catch(error => {
            logMessage(`Error refreshing product list: ${error.message}`, 'error');
        });
}

// Update the product list UI with new data
function updateProductListUI(listElement, products) {
    // Clear the current list
    listElement.innerHTML = '';
    
    // Create a new list with the updated products
    products.forEach(product => {
        const listItem = document.createElement('div');
        listItem.className = 'list-group-item product-item d-flex align-items-center';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'form-check-input me-3 product-checkbox';
        checkbox.value = product.psChildName;
        checkbox.dataset.name = product.displayName;
        checkbox.addEventListener('change', updateSelectedProducts);
        
        const nameContainer = document.createElement('div');
        nameContainer.className = 'ms-2 me-auto';
        
        const name = document.createElement('div');
        name.className = 'fw-bold';
        name.textContent = product.displayName;
        
        const publisher = document.createElement('div');
        publisher.className = 'small text-muted';
        publisher.textContent = product.publisher || 'Unknown Publisher';
        
        nameContainer.appendChild(name);
        nameContainer.appendChild(publisher);
        
        listItem.appendChild(checkbox);
        listItem.appendChild(nameContainer);
        
        listElement.appendChild(listItem);
    });
    
    // Reset selection state
    selectedProducts = [];
    updateSelectedProducts();
}

// Log a message to the log area
function logMessage(message, type = 'info') {
    if (!logArea) return;
    
    const logEntry = document.createElement('p');
    logEntry.className = `log-entry log-${type}`;
    
    // Add timestamp
    const now = new Date();
    const timestamp = `[${now.toLocaleTimeString()}] `;
    
    logEntry.textContent = timestamp + message;
    
    // Add to log area
    logArea.appendChild(logEntry);
    
    // Scroll to bottom
    logArea.scrollTop = logArea.scrollHeight;
}

// Show an alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    // Create the alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.role = 'alert';
    
    // Add the message
    alertElement.textContent = message;
    
    // Add the dismiss button
    const dismissButton = document.createElement('button');
    dismissButton.type = 'button';
    dismissButton.className = 'btn-close';
    dismissButton.dataset.bsDismiss = 'alert';
    dismissButton.setAttribute('aria-label', 'Close');
    
    alertElement.appendChild(dismissButton);
    
    // Add to the container
    alertContainer.appendChild(alertElement);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertElement.parentNode === alertContainer) {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }
    }, 5000);
}
