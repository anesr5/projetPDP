const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const form = document.getElementById("login-form")

form.addEventListener("submit", function(e){
    e.preventDefault(); /*Empêche la page de se recharger automatiquement et permet le bon envoi vers le backend*/ 

    const data = {
        email: document.getElementById("email").value,
        mdp: document.getElementById("mdp").value
    };

    fetch(`${API_BASE_URL}/login_entreprises`, {
        method: "POST", 
        headers:{
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log(result); // VOIR exactement ce que le backend renvoie

        const msg = document.getElementById("message");
        if(result.message === "Connexion réussie"){
            msg.className = "alert alert-success";
            msg.innerText = "✓ Connexion réussie ! Redirection...";
            localStorage.removeItem("etudiant_id");
            localStorage.setItem("entreprise_id", result.id);
            setTimeout(() => {
                window.location.href = "dashbord_entreprise.html";
            }, 1000);
        }
        else{
            msg.className = "alert alert-error";
            msg.innerText = Object.values(result)[0];
        }
    })
    .catch(error => {
        const msg = document.getElementById("message");
        msg.className = "alert alert-error";
        msg.innerText = "Erreur serveur — vérifiez que le backend est démarré.";
        console.error("Erreur", error);
    })
    
})
