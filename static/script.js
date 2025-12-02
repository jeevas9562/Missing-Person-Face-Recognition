// Toggle Login Form
document.getElementById('loginButton').addEventListener('click', function () {
    const loginContainer = document.getElementById('loginContainer');
// Show Login Form

    // Fetch the login content from Flask route
    fetch('/login')
      .then(response => {
        if (!response.ok) {
          throw new Error("Login page not found");
        }
        return response.text();
      })
      .then(data => {
        loginContainer.innerHTML = data;
        loginContainer.classList.add('visible');

        // Add event listener for the login form submission
        document.getElementById('loginForm').addEventListener('submit', function (event) {
          event.preventDefault();
          const username = document.getElementById('username').value;
          const password = document.getElementById('password').value;
          alert(`Username: ${username}\nPassword: ${password}`);
        });
      })
      .catch(error => console.error('Error loading login form:', error));
});

// Toggle Register Form
document.getElementById('registerButton').addEventListener('click', function () {
    const registerContainer = document.getElementById('registerContainer');

    // Fetch the register content from Flask route
    fetch('/register')
      .then(response => {
        if (!response.ok) {
          throw new Error("Register page not found");
        }
        return response.text();
      })
      .then(data => {
        registerContainer.innerHTML = data;
        registerContainer.classList.add('visible');

        // Add event listener for the register form submission
        document.getElementById('registerForm').addEventListener('submit', function (event) {
          event.preventDefault();
          const regUsername = document.getElementById('regUsername').value;
          const regPassword = document.getElementById('regPassword').value;
          alert(`Username: ${regUsername}\nPassword: ${regPassword}`);
        });
      })
      .catch(error => console.error('Error loading register form:', error));
});
