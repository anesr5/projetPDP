const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const entrepriseId = localStorage.getItem("entreprise_id");
let allCandidatures = [];
let companyOffres = [];

if (!entrepriseId) {
    window.location.href = "connexion_entreprise.html";
}

function statutBadge(statut) {
    const map = { "en attente": "badge-pending", "acceptée": "badge-accepted", "refusée": "badge-refused" };
    return `<span class="badge ${map[statut] || "badge-type"}">${statut}</span>`;
}

function cvLink(cv) {
    if (cv && cv.startsWith("data:application/pdf")) {
        return `<a href="${cv}" target="_blank" class="btn btn-ghost btn-sm" style="padding:0.2rem 0.5rem;font-size:0.78rem;">Lire le CV</a>`;
    }
    return `<span style="color:var(--text-muted);font-size:0.82rem;">${cv ? cv : "Aucun CV"}</span>`;
}

// Load company profile
fetch(`${API_BASE_URL}/entreprise/${entrepriseId}`)
    .then(r => r.json())
    .then(result => {
        document.getElementById("name").innerText = result.name || "—";
        document.getElementById("email").innerText = result.email || "—";
        const initiale = document.getElementById("avatar-initiale");
        if (initiale && result.name) initiale.innerText = result.name.charAt(0).toUpperCase();
    })
    .catch(() => {});

// Load offers separately (avoids SQLAlchemy ORM serialization issues)
fetch(`${API_BASE_URL}/offres`)
    .then(r => r.json())
    .then(allOffres => {
        companyOffres = Array.isArray(allOffres)
            ? allOffres.filter(o => o.entreprise_id === parseInt(entrepriseId))
            : [];
        document.getElementById("stat-offres").innerText = companyOffres.length;
        renderOffres(companyOffres);

        // Populate offer filter dropdown
        const select = document.getElementById("filtre-offre");
        companyOffres.forEach(o => {
            const opt = document.createElement("option");
            opt.value = o.titre;
            opt.textContent = o.titre;
            select.appendChild(opt);
        });
    })
    .catch(() => {
        document.getElementById("offres-list").innerHTML = `<div class="empty-state"><p>Impossible de charger les offres.</p></div>`;
    });

// Load candidatures
fetch(`${API_BASE_URL}/entreprise/${entrepriseId}/candidatures`)
    .then(r => r.json())
    .then(data => {
        allCandidatures = Array.isArray(data) ? data : [];

        const total = allCandidatures.length;
        const pending = allCandidatures.filter(c => c.statut === "en attente").length;
        const accepted = allCandidatures.filter(c => c.statut === "acceptée").length;

        document.getElementById("stat-total").innerText = total;
        document.getElementById("stat-pending").innerText = pending;
        document.getElementById("stat-accepted").innerText = accepted;

        const tabBadge = document.getElementById("cand-tab-badge");
        if (total > 0) { tabBadge.innerText = total; tabBadge.style.display = ""; }

        renderCandidatures(allCandidatures);
    })
    .catch(() => {
        document.getElementById("candidatures-container").innerHTML = `<div class="empty-state"><p>Impossible de charger les candidatures.</p></div>`;
    });

function renderOffres(offres) {
    const container = document.getElementById("offres-list");
    if (offres.length === 0) {
        container.innerHTML = `<div class="empty-state"><p>Aucune offre publiée pour le moment.</p><a href="poster_offre.html" class="btn btn-primary" style="margin-top:1rem;">Publier une offre</a></div>`;
        return;
    }
    container.innerHTML = "";
    offres.forEach(o => {
        const card = document.createElement("div");
        card.className = "offre-manage-card fade-in";
        card.innerHTML = `
            <div class="offre-manage-header">
                <div>
                    <span class="badge badge-type" style="margin-bottom:0.5rem;">${o.type || "Offre"}</span>
                    <h4>${o.titre}</h4>
                    <p style="font-size:0.82rem;color:var(--text-muted);margin-top:0.2rem;">${o.lieu} &nbsp;·&nbsp; ${o.duree} &nbsp;·&nbsp; à partir du ${o.debut}</p>
                </div>
                <div style="display:flex;gap:0.5rem;flex-shrink:0;">
                    <a href="poster_offre.html" class="btn btn-ghost btn-sm">Nouvelle offre</a>
                    <button class="btn btn-danger btn-sm" onclick="deleteOffre(${o.id})">Supprimer</button>
                </div>
            </div>
            <p style="font-size:0.82rem;color:var(--text-muted);margin:0.6rem 0 0.5rem;">Compétences : ${o.competences}</p>
            <p style="font-size:0.88rem;line-height:1.6;color:var(--text);">${o.description}</p>
        `;
        container.appendChild(card);
    });
}

function renderCandidatures(candidatures) {
    const container = document.getElementById("candidatures-container");
    if (candidatures.length === 0) {
        container.innerHTML = `<div class="empty-state"><p>Aucune candidature pour cette sélection.</p></div>`;
        return;
    }
    container.innerHTML = "";
    candidatures.forEach(c => {
        const card = document.createElement("div");
        card.className = "ent-cand-card fade-in";
        card.innerHTML = `
            <div class="ent-cand-header">
                <div>
                    <h4 style="font-size:1rem;font-weight:700;margin-bottom:0.2rem;">${c.etudiant_nom}</h4>
                    <p style="font-size:0.82rem;color:var(--text-muted);">Candidature pour <strong>${c.offre_titre}</strong></p>
                </div>
                ${statutBadge(c.statut)}
            </div>
            <div class="ent-cand-detail">
                <div><span style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;">Email</span><br><strong style="font-size:0.88rem;">${c.etudiant_email}</strong></div>
                <div><span style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;">CV</span><br>${cvLink(c.etudiant_cv)}</div>
            </div>
            <div class="ent-cand-actions">
                ${c.statut !== "acceptée" ? `<button class="btn btn-success btn-sm" onclick="changerStatut(${c.id}, 'acceptée')">Accepter</button>` : ""}
                ${c.statut !== "refusée" ? `<button class="btn btn-danger btn-sm" onclick="changerStatut(${c.id}, 'refusée')">Refuser</button>` : ""}
                ${c.statut !== "en attente" ? `<button class="btn btn-ghost btn-sm" onclick="changerStatut(${c.id}, 'en attente')">Remettre en attente</button>` : ""}
            </div>
        `;
        container.appendChild(card);
    });
}

function deleteOffre(offreId) {
    if (!confirm("Supprimer cette offre ? Les candidatures associées seront également supprimées.")) return;
    fetch(`${API_BASE_URL}/offres/${offreId}`, { method: "DELETE" })
        .then(r => r.json())
        .then(() => location.reload())
        .catch(err => console.error("Erreur suppression:", err));
}

function filtrerCandidatures() {
    const filtre = document.getElementById("filtre-offre").value;
    const filtered = filtre ? allCandidatures.filter(c => c.offre_titre === filtre) : allCandidatures;
    renderCandidatures(filtered);
}

function changerStatut(candidatureId, statut) {
    fetch(`${API_BASE_URL}/candidature/${candidatureId}/statut?nouveau_statut=${statut}`, { method: "PUT" })
        .then(r => r.json())
        .then(() => location.reload())
        .catch(err => console.error("Erreur:", err));
}

function switchTab(tab, btn) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    document.getElementById("tab-" + tab).classList.add("active");
    if (btn) btn.classList.add("active");
}

function ouvrirMessagerie() { window.location.href = "messagerie.html"; }
function logout() { localStorage.clear(); window.location.href = "index.html"; }
