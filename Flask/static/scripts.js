// Estrellas calificación
const starContainers = document.querySelectorAll('.stars');

starContainers.forEach(function(starContainer) {
    const stars = starContainer.querySelectorAll('.star');
    const id = starContainer.getAttribute('data-id');
    const inputCalificacion = document.getElementById('calificacion_pelicula_' + id) || document.getElementById('calificacion_serie_' + id);

    stars.forEach(function(star, index) {
        star.addEventListener('click', function() {
            // Actualiza las estrellas visualmente
            for (let i = 0; i <= index; i++) {
                stars[i].classList.add('checked');
            }
            for (let i = index + 1; i < stars.length; i++) {
                stars[i].classList.remove('checked');
            }

            // Actualiza el valor de la calificación
            inputCalificacion.value = index + 1;
        });
    });
});

// Detectar el cambio en el menú desplegable y enviar el formulario automáticamente
document.addEventListener('DOMContentLoaded', function () {
    const orderSelect = document.getElementById('orderSelect');
    const searchForm = document.getElementById('searchForm');

    if (orderSelect && searchForm) {
        orderSelect.addEventListener('change', function () {
            searchForm.submit();
        });
    }
});

// Mostrar/ocultar contraseña
document.addEventListener("DOMContentLoaded", function () {
    const togglePasswordButtons = document.querySelectorAll("#togglePassword");

    togglePasswordButtons.forEach(button => {
        button.addEventListener("click", function () {
            const passwordInput = this.previousElementSibling;
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                this.textContent = "Ocultar";
            } else {
                passwordInput.type = "password";
                this.textContent = "Mostrar";
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const emailInput = document.getElementById("email");
    const emailHelp = document.getElementById("emailHelp");

    const passwordInput = document.getElementById("password");
    const passwordHelp = document.getElementById("passwordHelp");

    const form = document.getElementById("registroForm");

    // Validación de email en tiempo real
    emailInput.addEventListener("input", function() {
        const email = emailInput.value;

        if (email.length > 5) {
            fetch("/verificar_email", {
                method: "POST",
                body: JSON.stringify({ email: email }),
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    emailHelp.textContent = "Este correo ya está registrado";
                    emailInput.classList.add("is-invalid");
                } else {
                    emailHelp.textContent = "";
                    emailInput.classList.remove("is-invalid");
                }
            });
        }
    });

    // Validación de la contraseña en tiempo real
    passwordInput.addEventListener("input", function() {
        const password = passwordInput.value;

        if (password.length < 6) {
            passwordHelp.textContent = "La contraseña debe tener al menos 6 caracteres";
            passwordInput.classList.add("is-invalid");
        } else {
            passwordHelp.textContent = "";
            passwordInput.classList.remove("is-invalid");
        }
    });

    // Validación antes de enviar el formulario
    form.addEventListener("submit", function(event) {
        let valid = true;

        if (emailInput.value.trim() === "") {
            emailHelp.textContent = "Este campo es obligatorio";
            emailInput.classList.add("is-invalid");
            valid = false;
        }

        if (passwordInput.value.trim() === "") {
            passwordHelp.textContent = "Este campo es obligatorio";
            passwordInput.classList.add("is-invalid");
            valid = false;
        } else if (passwordInput.value.length < 6) {
            passwordHelp.textContent = "La contraseña debe tener al menos 6 caracteres";
            passwordInput.classList.add("is-invalid");
            valid = false;
        }

        if (!valid) {
            event.preventDefault(); // Evita que el formulario se envíe si hay errores
        }
    });
});
