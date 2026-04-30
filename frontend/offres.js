const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
const id_etudiant = localStorage.getItem("etudiant_id");
let toutesLesOffres = [];
let studentSkills = new Set();

function calcScore(offreCompetences) {
    if (!studentSkills.size) return null;
    const offerSkills = new Set(
        offreCompetences.toLowerCase().replace(/,/g, ' ').split(/\s+/).filter(w => w.length > 1)
    );
    if (!offerSkills.size) return null;
    let common = 0;
    studentSkills.forEach(s => { if (offerSkills.has(s)) common++; });
    return Math.round(common / offerSkills.size * 100);
}

function scoreBadge(score) {
    if (score === null) return "";
    const color = score >= 70 ? "#059669" : score >= 40 ? "#d97706" : "#64748b";
    return `<span style="font-size:0.72rem;font-weight:700;color:${color};background:${color}18;border:1px solid ${color}33;border-radius:9999px;padding:0.2rem 0.6rem;">${score}% compatible</span>`;
}

document.addEventListener("DOMContentLoaded", () => {
    const loadOffres = () => fetch(`${API_BASE_URL}/offres`)
        .then(r => r.json())
        .then(data => { toutesLesOffres = data; afficherOffres(toutesLesOffres); })
        .catch(() => { document.getElementById("offres-container").innerHTML = `<div class="empty-state"><p>Impossible de charger les offres.</p></div>`; });

    if (id_etudiant) {
        fetch(`${API_BASE_URL}/etudiant/${id_etudiant}`)
            .then(r => r.json())
            .then(result => {
                if (result.competences) {
                    studentSkills = new Set(
                        result.competences.toLowerCase().replace(/,/g, ' ').split(/\s+/).filter(w => w.length > 1)
                    );
                }
            })
            .catch(() => {})
            .finally(() => loadOffres());
    } else {
        loadOffres();
    }
});

function afficherOffres(offres) {
    const container = document.getElementById("offres-container");
    const countEl = document.getElementById("offres-count");
    container.innerHTML = "";

    if (countEl) {
        countEl.textContent = offres.length + " offre" + (offres.length > 1 ? "s" : "") + " disponible" + (offres.length > 1 ? "s" : "");
    }

    if (offres.length === 0) {
        container.innerHTML = `<div class="empty-state" style="grid-column:1/-1;"><p>Aucune offre ne correspond à votre recherche.</p></div>`;
        return;
    }

    offres.forEach(offre => {
        const score = calcScore(offre.competences);
        const div = document.createElement("div");
        div.className = "offre-card fade-in";
        div.innerHTML = `
            <div class="offre-meta" style="justify-content:space-between;align-items:center;">
                <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
                    <span class="badge badge-type">${offre.type || "Offre"}</span>
                    <span class="badge" style="background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;">${offre.lieu}</span>
                    <span class="badge" style="background:#faf5ff;color:#6b21a8;border:1px solid #e9d5ff;">${offre.duree}</span>
                </div>
                ${scoreBadge(score)}
            </div>
            <h3 style="margin-bottom:0.5rem;">${offre.titre}</h3>
            <p class="offre-description">${offre.description}</p>
            <div style="font-size:0.82rem;color:var(--text-muted);margin-bottom:1rem;">
                Début : <strong>${offre.debut}</strong> &nbsp;·&nbsp; ${offre.competences}
            </div>
            <button class="btn btn-primary btn-sm" onclick="postuler(${offre.id})">Postuler →</button>
        `;
        container.appendChild(div);
    });
}

function filtrerOffres() {
    const searchTerm = document.getElementById("searchInput").value.toLowerCase();
    const offresFiltrees = toutesLesOffres.filter(offre =>
        offre.titre.toLowerCase().includes(searchTerm) ||
        offre.description.toLowerCase().includes(searchTerm) ||
        offre.lieu.toLowerCase().includes(searchTerm) ||
        offre.competences.toLowerCase().includes(searchTerm)
    );
    afficherOffres(offresFiltrees);
}

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("searchInput");
    if (input) input.addEventListener("keyup", e => { if (e.key === "Enter") filtrerOffres(); });
});

function postuler(offreId) {
    const etudiantId = localStorage.getItem("etudiant_id");
    if (!etudiantId) {
        alert("Vous devez être connecté !");
        return;
    }
    fetch(`${API_BASE_URL}/postuler`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ etudiant_id: parseInt(etudiantId), offre_id: offreId })
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            window.location.href = "dashbord.html";
        }
    })
    .catch(error => console.error("Erreur :", error));
}

function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}
