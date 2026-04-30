const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const userId = localStorage.getItem("etudiant_id") || localStorage.getItem("entreprise_id");
const role = localStorage.getItem("etudiant_id") ? "etudiant" : "entreprise";
const messageForm = document.getElementById("formMessage");
const messageInput = document.getElementById("contenu");
const destinataireInput = document.getElementById("destinataire_id");
const container = document.getElementById("messages-container");

window.addEventListener("DOMContentLoaded", () => {
    const etudiantId = localStorage.getItem("etudiant_id");
    const entrepriseId = localStorage.getItem("entreprise_id");

    if (!etudiantId && !entrepriseId) {
        alert("Vous devez être connecté !");
        window.location.href = "index.html"; // retour accueil si pas connecté
    }
});


document.getElementById("formMessage").addEventListener("submit", async (e) => {
    e.preventDefault();

    const contenu = document.getElementById("contenu").value;
    const destinataire_email = document.getElementById("destinataire_email").value;
    const expediteur_id = localStorage.getItem("etudiant_id") || localStorage.getItem("entreprise_id");
    const expediteur_type = localStorage.getItem("etudiant_id") ? "etudiant" : "entreprise";

    const data = {
        contenu,
        destinataire_email,
        expediteur_id: parseInt(expediteur_id),
        expediteur_type
    };

    try {
        const res = await fetch(`${API_BASE_URL}/message/email`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await res.json();
        alert(result.message || "Message envoyé !");
        document.getElementById("formMessage").reset();
    } catch (error) {
        console.error("Erreur:", error);
        alert("Erreur lors de l'envoi du message.");
    }
});

// Chargement des messages
async function chargerMessages() {
    console.log("ID connecté :", userId);  // ← il doit être égal à 1 ici

    try {
        const res = await fetch(`${API_BASE_URL}/messages/${userId}`);
        const messages = await res.json();

        container.innerHTML = "";

        if (messages.length === 0) {
            container.innerHTML = `<div class="empty-state"><p>Aucun message reçu pour le moment.</p></div>`;
            return;
        }

        messages.forEach(m => {
            const div = document.createElement("div");
            div.classList.add("message-card", "fade-in");
            div.innerHTML = `
                <div class="message-meta">De : <strong>${m.expediteur}</strong> &nbsp;→&nbsp; <strong>${m.destinataire}</strong></div>
                <p style="font-size:0.92rem;color:var(--text);margin-top:0.25rem;">${m.contenu}</p>
            `;
            container.appendChild(div);
        });

    } catch (err) {
        console.error("Erreur chargement messages :", err);
    }
}

// Charger les messages au chargement de la page
window.addEventListener("DOMContentLoaded", chargerMessages);
