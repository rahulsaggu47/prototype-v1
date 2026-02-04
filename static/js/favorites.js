const grid = document.getElementById("favoritesGrid");
const emptyState = document.getElementById("favoritesEmpty");
const filterButtons = document.querySelectorAll(".favorites-filters button");

let currentType = "all";

// 🔹 initial load
fetchFavorites();

// 🔹 filter buttons
filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        filterButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        currentType = btn.dataset.type;
        fetchFavorites();
    });
});

// 🔹 fetch favorites from backend
function fetchFavorites() {
    let url = "/api/favorites";
    if (currentType !== "all") {
        url += `?type=${currentType}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(data => renderFavorites(data));
}

// 🔹 render favorites
function renderFavorites(items) {
    grid.innerHTML = "";

    if (!items || items.length === 0) {
        emptyState.classList.remove("hidden");
        return;
    }

    emptyState.classList.add("hidden");

    items.forEach((item, index) => {
        const card = document.createElement("div");
        card.className = "content-card";
        card.dataset.id = item.id;

        card.style.setProperty("--delay", `${index * 40}ms`);

        card.innerHTML = `
            <img src="${item.poster_url}" alt="${item.title}">
            <div class="card-overlay">
                <h3>${item.title}</h3>
                <button class="card-fav-btn" title="Remove from favorites">❤️</button>
            </div>
        `;

        grid.appendChild(card);
    });
}

// 🔹 click handling (event delegation)
grid.addEventListener("click", async (e) => {
    const favBtn = e.target.closest(".card-fav-btn");
    const card = e.target.closest(".content-card");

    // ❤️ remove favorite
    if (favBtn && card) {
        e.stopPropagation();

        const contentId = card.dataset.id;

        await fetch("/api/favorites/remove", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content_id: contentId })
        });

        // animate out
        card.classList.add("fade-out");
        setTimeout(() => {
            card.remove();
            if (grid.children.length === 0) {
                emptyState.classList.remove("hidden");
            }
        }, 250);

        return;
    }

    // 🎬 open detail page
    if (card) {
        const contentId = card.dataset.id;
        window.location.href = `/content/${contentId}`;
    }
});
