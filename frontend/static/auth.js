document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const errorMessage = document.getElementById('errorMessage');

    // Login form handler
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            hideError();

            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;

            if (!username || !password) {
                showError('Please fill in all fields');
                return;
            }

            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const buttonText = submitBtn.querySelector('.button-text');
            const buttonLoader = submitBtn.querySelector('.button-loader');

            submitBtn.disabled = true;
            buttonText.style.display = 'none';
            buttonLoader.style.display = 'flex';

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    window.location.href = '/dashboard';
                } else {
                    showError(data.error || 'Invalid username or password');
                }
            } catch (error) {
                console.error('Login error:', error);
                showError('Login failed. Please try again.');
            } finally {
                submitBtn.disabled = false;
                buttonText.style.display = 'inline';
                buttonLoader.style.display = 'none';
            }
        });
    }

    // Register form handler
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            hideError();

            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;

            // Validation
            if (!username || !email || !password) {
                showError('Please fill in all fields');
                return;
            }

            if (username.length < 3) {
                showError('Username must be at least 3 characters');
                return;
            }

            if (password.length < 6) {
                showError('Password must be at least 6 characters');
                return;
            }

            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const buttonText = submitBtn.querySelector('.button-text');
            const buttonLoader = submitBtn.querySelector('.button-loader');

            submitBtn.disabled = true;
            buttonText.style.display = 'none';
            buttonLoader.style.display = 'flex';

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    window.location.href = '/dashboard';
                } else {
                    showError(data.error || 'Registration failed');
                }
            } catch (error) {
                console.error('Registration error:', error);
                showError('Registration failed. Please try again.');
            } finally {
                submitBtn.disabled = false;
                buttonText.style.display = 'inline';
                buttonLoader.style.display = 'none';
            }
        });
    }

    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    function hideError() {
        if (errorMessage) {
            errorMessage.style.display = 'none';
        }
    }
});
