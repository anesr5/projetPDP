const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const id = localStorage.getItem("etudiant_id");

if (!id) { window.location.href = "connexion.html"; }

function statutBadge(statut) {
    const map = { "en attente": "badge-pending", "acceptée": "badge-accepted", "refusée": "badge-refused" };
    return `<span class="badge ${map[statut] || "badge-type"}">${statut}</span>`;
}

function scoreBadge(score) {
    const color = score >= 70 ? "#059669" : score >= 40 ? "#d97706" : "#64748b";
    return `<span style="font-size:0.72rem;font-weight:700;color:${color};background:${color}18;border:1px solid ${color}33;border-radius:9999px;padding:0.2rem 0.6rem;">${score}% compatible</span>`;
}

function switchTab(tab, btn) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    document.getElementById("tab-" + tab).classList.add("active");
    if (btn) btn.classList.add("active");
}

fetch(`${API_BASE_URL}/etudiant/${id}`)
    .then(response => response.json())
    .then(result => {
        document.getElementById("name").innerText = result.name;
        document.getElementById("email").innerText = result.email;
        document.getElementById("age").innerText = result.age + " ans";

        const cvEl = document.getElementById("cv");
        if (result.cv && result.cv.startsWith("data:application/pdf")) {
            cvEl.innerHTML = `<a href="${result.cv}" target="_blank" class="btn btn-ghost btn-sm" style="padding:0.25rem 0.6rem;">Voir le CV</a>`;
        } else {
            cvEl.textContent = result.cv || "—";
        }

        const compEl = document.getElementById("competences");
        compEl.textContent = result.competences || "—";
        if (result.competences) {
            document.getElementById("competences-input").value = result.competences;
        }

        const initiale = document.getElementById("avatar-initiale");
        if (initiale && result.name) initiale.innerText = result.name.charAt(0).toUpperCase();

        fetch(`${API_BASE_URL}/candidatures/${id}`)
            .then(res => res.json())
            .then(candidatures => {
                const container = document.getElementById("liste-candidatures");
                const badge = document.getElementById("count-badge");
                if (candidatures.length === 0) {
                    container.innerHTML = `<div class="empty-state"><p>Aucune candidature pour le moment.<br>Explorez les offres disponibles.</p></div>`;
                } else {
                    if (badge) { badge.innerText = candidatures.length; badge.style.display = ""; }
                    container.innerHTML = "";
                    candidatures.forEach(c => {
                        const card = document.createElement("div");
                        card.className = "candidature-card fade-in";
                        card.innerHTML = `
                            <div class="candidature-info">
                                <h4>${c.titre}</h4>
                                <p>${c.lieu} &nbsp;·&nbsp; ${c.debut}</p>
                                <p style="margin-top:0.25rem;">${c.description}</p>
                            </div>
                            <div style="flex-shrink:0;">${statutBadge(c.statut)}</div>
                        `;
                        container.appendChild(card);
                    });
                }
            });
    })
    .catch(error => console.error("Erreur:", error));

// Load AI recommendations + analysis
fetch(`${API_BASE_URL}/etudiant/${id}/recommandations`)
    .then(r => r.json())
    .then(offres => {
        const container = document.getElementById("liste-recommandations");
        if (!offres || offres.length === 0) {
            container.innerHTML = `<div class="empty-state"><p>Ajoutez vos compétences pour obtenir des recommandations personnalisées.</p></div>`;
            return;
        }
        container.innerHTML = "";
        offres.forEach(o => {
            const card = document.createElement("div");
            card.className = "offre-manage-card fade-in";
            card.innerHTML = `
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;margin-bottom:0.5rem;">
                    <div>
                        <span class="badge badge-type" style="margin-bottom:0.4rem;">${o.type || "Offre"}</span>
                        <h4 style="font-size:0.95rem;font-weight:700;">${o.titre}</h4>
                        <p style="font-size:0.8rem;color:var(--text-muted);margin-top:0.15rem;">${o.lieu} &nbsp;·&nbsp; ${o.duree}</p>
                    </div>
                    ${scoreBadge(o.score)}
                </div>
                <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:0.5rem;">Compétences requises : ${o.competences}</p>
                <a href="offres.html" class="btn btn-primary btn-sm">Voir les offres</a>
            `;
            container.appendChild(card);
        });
    })
    .catch(() => {
        document.getElementById("liste-recommandations").innerHTML = `<div class="empty-state"><p>Impossible de charger les recommandations.</p></div>`;
    });

fetch(`${API_BASE_URL}/etudiant/${id}/analyse`)
    .then(r => r.json())
    .then(analyse => {
        const el = document.getElementById("ia-analyse");
        const scoreColor = analyse.profile_score >= 80 ? "#059669" : analyse.profile_score >= 50 ? "#d97706" : "#ef4444";
        const compatColor = analyse.compatibilite_moyenne >= 60 ? "#059669" : analyse.compatibilite_moyenne >= 30 ? "#d97706" : "#64748b";
        const tags = [...analyse.competences_detectees, ...analyse.mots_cles]
            .map(k => `<span style="display:inline-block;background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.18);color:var(--primary);border-radius:9999px;padding:0.15rem 0.55rem;font-size:0.72rem;font-weight:600;margin:0.15rem;">${k}</span>`)
            .join("");
        el.innerHTML = `
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:0.5rem;">
                <div style="text-align:center;">
                    <div style="font-size:2rem;font-weight:800;color:${scoreColor};">${analyse.profile_score}%</div>
                    <div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;margin-top:0.15rem;">Profil complété</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:2rem;font-weight:800;color:${compatColor};">${analyse.compatibilite_moyenne}%</div>
                    <div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;margin-top:0.15rem;">Compatibilité moyenne</div>
                </div>
            </div>
            ${tags ? `<div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1rem;">
                <p style="font-size:0.72rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">${analyse.nb_competences} compétence(s) détectée(s)</p>
                <div>${tags}</div>
            </div>` : `<div class="empty-state" style="padding:1rem;"><p>Ajoutez vos compétences dans la sidebar pour voir votre analyse.</p></div>`}
        `;
    })
    .catch(() => {});

document.getElementById("cv-update-input").addEventListener("change", function() {
    const file = this.files[0];
    const display = document.getElementById("cv-update-name");
    if (file) {
        display.textContent = file.name;
        display.style.color = "var(--primary)";
    } else {
        display.textContent = "Choisir un PDF...";
        display.style.color = "";
    }
});

function updateCV() {
    const msgEl = document.getElementById("cv-update-msg");
    const file = document.getElementById("cv-update-input").files[0];
    if (!file) {
        msgEl.className = "alert alert-error"; msgEl.textContent = "Sélectionnez un fichier PDF."; return;
    }
    if (file.type !== "application/pdf") {
        msgEl.className = "alert alert-error"; msgEl.textContent = "Format PDF uniquement."; return;
    }
    if (file.size > 5 * 1024 * 1024) {
        msgEl.className = "alert alert-error"; msgEl.textContent = "Fichier trop volumineux (max 5 Mo)."; return;
    }
    msgEl.className = ""; msgEl.textContent = "Envoi en cours...";
    const reader = new FileReader();
    reader.onload = async function(evt) {
        try {
            const res = await fetch(`${API_BASE_URL}/etudiant/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ cv: evt.target.result })
            });
            if (res.ok) {
                document.getElementById("cv").innerHTML = `<a href="${evt.target.result}" target="_blank" class="btn btn-ghost btn-sm" style="padding:0.25rem 0.6rem;">Voir le CV</a>`;
                msgEl.className = ""; msgEl.textContent = "Analyse du CV en cours...";
                try {
                    const extRes = await fetch(`${API_BASE_URL}/extraire-cv`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ cv: evt.target.result })
                    });
                    const extData = await extRes.json();
                    if (extData.competences && extData.competences.length > 0) {
                        const currentVal = document.getElementById("competences-input").value.trim();
                        const currentSet = new Set(currentVal.toLowerCase().split(/,\s*/).filter(Boolean));
                        const toAdd = extData.competences.filter(c => !currentSet.has(c));
                        const merged = currentVal
                            ? (toAdd.length > 0 ? currentVal + ", " + toAdd.join(", ") : currentVal)
                            : extData.competences.join(", ");
                        document.getElementById("competences-input").value = merged;
                        document.getElementById("competences").textContent = merged;
                        msgEl.className = "alert alert-success";
                        msgEl.textContent = `CV mis à jour. ${extData.nb} compétence(s) détectée(s) automatiquement.`;
                    } else {
                        msgEl.className = "alert alert-success";
                        msgEl.textContent = "CV mis à jour. Aucune compétence tech détectée — renseignez-les manuellement.";
                    }
                } catch(e) {
                    msgEl.className = "alert alert-success"; msgEl.textContent = "CV mis à jour.";
                }
            } else {
                msgEl.className = "alert alert-error"; msgEl.textContent = "Erreur lors de la mise à jour.";
            }
        } catch(e) {
            msgEl.className = "alert alert-error"; msgEl.textContent = "Erreur serveur.";
        }
    };
    reader.readAsDataURL(file);
}

async function updateCompetences() {
    const msgEl = document.getElementById("comp-update-msg");
    const val = document.getElementById("competences-input").value.trim();
    msgEl.className = ""; msgEl.textContent = "Enregistrement...";
    try {
        const res = await fetch(`${API_BASE_URL}/etudiant/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ competences: val })
        });
        if (res.ok) {
            msgEl.className = "alert alert-success"; msgEl.textContent = "Compétences mises à jour.";
            document.getElementById("competences").textContent = val || "—";
        } else {
            msgEl.className = "alert alert-error"; msgEl.textContent = "Erreur lors de la mise à jour.";
        }
    } catch(e) {
        msgEl.className = "alert alert-error"; msgEl.textContent = "Erreur serveur.";
    }
}

function ouvrirMessagerie() {
    window.location.href = "messagerie.html";
}

function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}

