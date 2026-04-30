const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const form = document.getElementById("OffrePost");

form.addEventListener("submit", function (e) {
    e.preventDefault(); // empêche le rechargement

    const entreprise_id = localStorage.getItem("entreprise_id"); // récupéré au login
    if (!entreprise_id) {
        alert("Erreur : entreprise non connectée !");
        return;
    }

    const data = {
        titre: document.getElementById("title").value,
        description: document.getElementById("description").value,
        type: document.getElementById("type").value,
        competences: document.getElementById("competences").value,
        duree: document.getElementById("duree").value,
        debut: document.getElementById("debut").value,
        lieu: document.getElementById("lieu").value,
        entreprise_id: parseInt(entreprise_id)
    };

    fetch(`${API_BASE_URL}/offres`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Erreur lors de l'envoi");
            }
            return response.json();
        })
        .then(result => {
            window.location.href = "dashbord_entreprise.html";
        })
        .catch(error => {
            console.error("Erreur :", error);
            alert("Échec de l'envoi de l'offre");
        });
});
