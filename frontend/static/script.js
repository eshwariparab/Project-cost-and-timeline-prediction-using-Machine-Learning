document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const projectTypeToggle = document.getElementById('projectTypeToggle');
    const constructionSection = document.getElementById('constructionSection');
    const softwareSection = document.getElementById('softwareSection');
    const constructionForm = document.getElementById('constructionForm');
    const softwareForm = document.getElementById('softwareForm');
    const constructionLabel = document.getElementById('constructionLabel');
    const softwareLabel = document.getElementById('softwareLabel');
    const resultsContainer = document.getElementById('resultsContainer');
    const errorMessage = document.getElementById('errorMessage');
    const viewHistoryBtn = document.getElementById('viewHistory');
    const historyContainer = document.getElementById('historyContainer');
    const historyList = document.getElementById('historyList');

    let currentProjectType = 'construction';

    // Toggle switch handler
    if (projectTypeToggle) {
        projectTypeToggle.addEventListener('change', function() {
            if (this.checked) {
                // Switch to Software
                currentProjectType = 'software';
                constructionSection.classList.remove('active');
                softwareSection.classList.add('active');
                constructionLabel.classList.remove('active');
                softwareLabel.classList.add('active');
            } else {
                // Switch to Construction
                currentProjectType = 'construction';
                softwareSection.classList.remove('active');
                constructionSection.classList.add('active');
                softwareLabel.classList.remove('active');
                constructionLabel.classList.add('active');
            }
            // Hide results when switching
            if (resultsContainer) resultsContainer.style.display = 'none';
            if (historyContainer) historyContainer.style.display = 'none';
        });

        // Initialize labels
        constructionLabel.classList.add('active');
    }

    // Construction form submission
    if (constructionForm) {
        constructionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await handleFormSubmission('construction', this);
        });
    }

    // Software form submission
    if (softwareForm) {
        softwareForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await handleFormSubmission('software', this);
        });
    }

    // Generic form submission handler
    async function handleFormSubmission(type, formElement) {
        // Hide previous results, errors, and history
        if (resultsContainer) resultsContainer.style.display = 'none';
        if (historyContainer) historyContainer.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'none';

        let formData = {};
        const submitButton = formElement.querySelector('button[type="submit"]');
        const buttonText = submitButton.querySelector('.button-text');
        const buttonLoader = submitButton.querySelector('.button-loader');

        // Get form values based on type
        if (type === 'construction') {
            formData = {
                project_type: 'construction',
                project_size_sqft: parseFloat(document.getElementById('project_size_sqft').value),
                num_workers: parseFloat(document.getElementById('num_workers').value),
                material_quality: parseFloat(document.getElementById('material_quality').value),
                project_complexity: parseFloat(document.getElementById('project_complexity').value),
                equipment_count: parseFloat(document.getElementById('equipment_count').value),
                team_experience_years: parseFloat(document.getElementById('team_experience_years').value)
            };

            if (!validateConstructionInputs(formData)) {
                return;
            }
        } else { // software
            formData = {
                project_type: 'software',
                team_exp: parseFloat(document.getElementById('team_exp').value),
                manager_exp: parseFloat(document.getElementById('manager_exp').value),
                transactions: parseFloat(document.getElementById('transactions').value),
                entities: parseFloat(document.getElementById('entities').value),
                points_non_adjust: parseFloat(document.getElementById('points_non_adjust').value),
                adjustment: parseFloat(document.getElementById('adjustment').value),
                language_level: parseFloat(document.getElementById('language').value)
            };

            if (!validateSoftwareInputs(formData)) {
                return;
            }
        }

        // Show loading state
        submitButton.disabled = true;
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'flex';

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData),
                credentials: 'same-origin'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            displayResults(data);

        } catch (error) {
            console.error('Prediction error:', error);
            showError(error.message || 'Failed to get prediction. Please check your inputs and try again.');
        } finally {
            submitButton.disabled = false;
            buttonText.style.display = 'inline';
            buttonLoader.style.display = 'none';
        }
    }

    function validateConstructionInputs(data) {
        const errors = [];

        if (isNaN(data.project_size_sqft) || data.project_size_sqft < 100) {
            errors.push('Project size must be at least 100 sq. ft.');
        }

        if (isNaN(data.num_workers) || data.num_workers < 1) {
            errors.push('Number of workers must be at least 1');
        }

        if (isNaN(data.material_quality) || data.material_quality < 1 || data.material_quality > 3) {
            errors.push('Material quality must be between 1 and 3');
        }

        if (isNaN(data.project_complexity) || data.project_complexity < 1 || data.project_complexity > 5) {
            errors.push('Project complexity must be between 1 and 5');
        }

        if (isNaN(data.equipment_count) || data.equipment_count < 0) {
            errors.push('Equipment count must be 0 or more');
        }

        if (isNaN(data.team_experience_years) || data.team_experience_years < 0) {
            errors.push('Team experience (years) must be 0 or more');
        }

        if (errors.length > 0) {
            showError(errors.join('<br>'));
            return false;
        }

        return true;
    }

    function validateSoftwareInputs(data) {
        const errors = [];

        // Dataset ranges (Software_Effort_ML_500): TeamExp 2-9, ManagerExp 3-9, Adjustment ~0.80-1.50, LanguageLevel 1-3
        if (isNaN(data.team_exp) || data.team_exp < 2 || data.team_exp > 9) {
            errors.push('Team experience must be between 2 and 9');
        }

        if (isNaN(data.manager_exp) || data.manager_exp < 3 || data.manager_exp > 9) {
            errors.push('Manager experience must be between 3 and 9');
        }

        if (isNaN(data.transactions) || data.transactions < 1) {
            errors.push('Transactions must be at least 1');
        }

        if (isNaN(data.entities) || data.entities < 1) {
            errors.push('Entities must be at least 1');
        }

        if (isNaN(data.points_non_adjust) || data.points_non_adjust < 1) {
            errors.push('Function points (non-adjusted) must be at least 1');
        }

        if (isNaN(data.adjustment) || data.adjustment < 0.8 || data.adjustment > 1.5) {
            errors.push('Adjustment factor must be between 0.80 and 1.50');
        }

        const lang = data.language_level !== undefined ? data.language_level : data.language;
        if (isNaN(lang) || lang < 1 || lang > 3) {
            errors.push('Language must be 1, 2, or 3');
        }

        if (errors.length > 0) {
            showError(errors.join('<br>'));
            return false;
        }

        return true;
    }

    function displayResults(data) {
        if (!resultsContainer) return;

        const costVal = data.predicted_cost ?? data.predicted_effort;
        const timeVal = data.predicted_time ?? (data.predicted_effort != null ? data.predicted_effort / 8 : null);
        const cost = formatCurrency(costVal);
        const time = formatTime(timeVal);

        document.getElementById('predicted_cost').textContent = cost;
        document.getElementById('predicted_time').textContent = time;

        resultsContainer.style.display = 'block';
        if (historyContainer) historyContainer.style.display = 'none';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        if (viewHistoryBtn) {
            setTimeout(loadHistory, 1000);
        }
    }

    function formatCurrency(amount) {
        if (amount == null || isNaN(amount)) return '₹0';
        return '₹' + Number(amount).toLocaleString('en-IN', {
            maximumFractionDigits: 0
        });
    }

    function formatTime(days) {
        if (days == null || isNaN(days)) return '0 days';
        const roundedDays = Math.round(days);
        if (roundedDays === 1) {
            return '1 day';
        } else if (roundedDays < 30) {
            return `${roundedDays} days`;
        } else {
            const months = Math.floor(roundedDays / 30);
            const remainingDays = roundedDays % 30;
            if (remainingDays === 0) {
                return months === 1 ? '1 month' : `${months} months`;
            } else {
                return `${months} month${months > 1 ? 's' : ''} ${remainingDays} day${remainingDays > 1 ? 's' : ''}`;
            }
        }
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function showError(message) {
        if (errorMessage) {
            errorMessage.innerHTML = message;
            errorMessage.style.display = 'block';
            if (resultsContainer) resultsContainer.style.display = 'block';
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    // View history button handler
    if (viewHistoryBtn) {
        viewHistoryBtn.addEventListener('click', async function() {
            if (historyContainer.style.display === 'none' || !historyContainer.style.display) {
                await loadHistory();
                historyContainer.style.display = 'block';
                if (resultsContainer) resultsContainer.style.display = 'none';
                historyContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                historyContainer.style.display = 'none';
            }
        });
    }

    // Load prediction history
    async function loadHistory() {
        try {
            const response = await fetch('/predictions', {
                method: 'GET',
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error('Failed to load history');
            }

            const data = await response.json();
            displayHistory(data.predictions || []);
        } catch (error) {
            console.error('History load error:', error);
            if (historyList) {
                historyList.innerHTML = '<div class="error-message">Failed to load prediction history</div>';
            }
        }
    }

    // Display history
    function displayHistory(predictions) {
        if (!historyList) return;

        if (predictions.length === 0) {
            historyList.innerHTML = '<div class="no-history">No predictions yet. Make your first prediction!</div>';
            return;
        }

        historyList.innerHTML = predictions.map(pred => `
            <div class="history-item">
                <div class="history-header">
                    <span class="history-type">${capitalizeFirst(pred.project_type)}</span>
                    <span class="history-date">${formatDate(pred.created_at)}</span>
                </div>
                <div class="history-details">
                    <div class="history-info">
                        <div><strong>Type:</strong> ${capitalizeFirst(pred.project_type)}</div>
                        <div><strong>Size:</strong> ${pred.project_size}</div>
                        <div><strong>Complexity:</strong> ${pred.complexity}</div>
                    </div>
                    <div class="history-results">
                        <div class="history-cost">Cost: ${formatCurrency(pred.predicted_cost)}</div>
                        <div class="history-time">Time: ${formatTime(pred.predicted_time)}</div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Add input validation on blur
    const forms = [constructionForm, softwareForm].filter(f => f);
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.value && !this.checkValidity()) {
                    this.style.borderColor = '#ef4444';
                } else {
                    this.style.borderColor = '';
                }
            });

            if (input.type === 'number') {
                input.addEventListener('input', function() {
                    if (this.value && !isNaN(this.value) && this.value >= 0) {
                        this.style.borderColor = '';
                    }
                });
            }
        });
    });
});
