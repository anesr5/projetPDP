const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const form = document.getElementById('formInscription');
const messageRetour = document.getElementById('messageRetour');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        email: document.getElementById('email').value,
        mdp: document.getElementById('mdp').value,
        name: document.getElementById('name').value,
    };

    try {
        const response = await fetch(`${API_BASE_URL}/inscription-entreprise`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            messageRetour.className = "alert alert-success";
            messageRetour.textContent = "✓ Compte créé avec succès ! Redirection...";
            setTimeout(()=>{ window.location.href="index.html"; }, 1200);
        } else {
            messageRetour.className = "alert alert-error";
            messageRetour.textContent = "Erreur lors de l'inscription. Vérifiez vos informations.";
        }
    } catch (error) {
        console.error('Erreur :', error);
        messageRetour.className = "alert alert-error";
        messageRetour.textContent = "Erreur serveur — vérifiez que le backend est démarré.";
    }
});
