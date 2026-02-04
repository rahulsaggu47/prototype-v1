(() => {
    const form = document.getElementById("searchForm");
    const input = document.getElementById("searchInput");
    const clearBtn = document.getElementById("clearSearch");
    const grid = document.getElementById("contentGrid");

    if (!form || !input || !grid) return;

    let debounceTimer = null;

    input.addEventListener("input", () => {
        clearBtn.style.display = input.value ? "block" : "none";
    });

    clearBtn.addEventListener("click", () => {
        grid.innerHTML = "";
        input.value = "";
        clearBtn.style.display = "none";

        window.SpotlightControl?.start();
    });

    document.addEventListener("keydown", e => {
        if (e.key === "Escape" && input.value) clearBtn.click();
    });

    form.addEventListener("submit", e => {
        e.preventDefault();
        runSearch(input.value.trim());
    });

    input.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            runSearch(input.value.trim());
        }, 300);
    });

    function runSearch(query) {
        if (!query) return;

        window.SpotlightControl?.stop();

        fetch(`/api/content?q=${query}&type=${form.dataset.type}`)
            .then(res => res.json())
            .then(render);
    }

    function render(items) {
        grid.innerHTML = "";

        if (!items.length) {
            grid.innerHTML = "<p class='no-results'>No results found</p>";
            return;
        }

        items.forEach(item => {
            const card = document.createElement("div");
            card.className = "content-card";
            card.innerHTML = `
                <img src="${item.poster_url}">
                <h3>${item.title}</h3>
            `;
            grid.appendChild(card);
        });
    }
})();
