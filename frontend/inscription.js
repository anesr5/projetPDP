const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const form = document.getElementById('formInscription');
const messageRetour = document.getElementById('messageRetour');

document.getElementById('cv').addEventListener('change', function() {
    const file = this.files[0];
    const display = document.getElementById('file-name-display');
    const compInput = document.getElementById('competences');
    if (!file) {
        display.textContent = 'Choisir un fichier PDF...';
        display.style.color = '';
        return;
    }
    display.textContent = file.name;
    display.style.color = 'var(--primary)';

    if (file.type !== 'application/pdf') return;

    const reader = new FileReader();
    reader.onload = async function(evt) {
        try {
            compInput.placeholder = 'Analyse en cours...';
            const res = await fetch(`${API_BASE_URL}/extraire-cv`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cv: evt.target.result })
            });
            const data = await res.json();
            if (data.competences && data.competences.length > 0) {
                const currentVal = compInput.value.trim();
                const currentSet = new Set(currentVal.toLowerCase().split(/,\s*/).filter(Boolean));
                const toAdd = data.competences.filter(c => !currentSet.has(c));
                compInput.value = currentVal
                    ? (toAdd.length > 0 ? currentVal + ', ' + toAdd.join(', ') : currentVal)
                    : data.competences.join(', ');
                compInput.placeholder = `${data.nb} compétence(s) détectée(s)`;
            } else {
                compInput.placeholder = 'Python, React, SQL...';
            }
        } catch(e) {
            compInput.placeholder = 'Python, React, SQL...';
        }
    };
    reader.readAsDataURL(file);
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const cvFile = document.getElementById('cv').files[0];
    if (!cvFile) {
        messageRetour.className = "alert alert-error";
        messageRetour.textContent = "Veuillez sélectionner votre CV en format PDF.";
        return;
    }
    if (cvFile.type !== 'application/pdf') {
        messageRetour.className = "alert alert-error";
        messageRetour.textContent = "Le fichier doit être au format PDF.";
        return;
    }
    if (cvFile.size > 5 * 1024 * 1024) {
        messageRetour.className = "alert alert-error";
        messageRetour.textContent = "Le fichier PDF ne doit pas dépasser 5 Mo.";
        return;
    }

    messageRetour.className = "";
    messageRetour.innerHTML = '<span class="spinner"></span> Envoi en cours...';

    const reader = new FileReader();
    reader.onload = async function(evt) {
        const cvBase64 = evt.target.result;
        const data = {
            email: document.getElementById('email').value,
            mdp: document.getElementById('mdp').value,
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            cv: cvBase64,
            lettre_motiv: "",
            competences: document.getElementById('competences').value.trim()
        };

        try {
            const response = await fetch(`${API_BASE_URL}/inscription-etudiant`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
    };
    reader.readAsDataURL(cvFile);
});
