(() => {
    const spotlightSection = document.getElementById("spotlight");
    if (!spotlightSection) return;

    let items = [];
    let index = 0;
    let timer = null;

    const type = spotlightSection.dataset.type;

    function render() {
        const item = items[index];

        document.getElementById("spotlightTitle").textContent = item.title;
        document.getElementById("spotlightDesc").textContent =
            item.description?.slice(0, 200) + "...";

        document.getElementById("spotlightPoster").src = item.poster_url;
        document.getElementById("detailsBtn").href = `/content/${item.id}`;

        const bg = item.background_url?.trim() || item.poster_url;
        spotlightSection.style.backgroundImage = `url(${bg})`;
    }

    function next() {
        index = (index + 1) % items.length;
        render();
    }

    function prev() {
        index = (index - 1 + items.length) % items.length;
        render();
    }

    function start() {
        stop();
        timer = setInterval(next, 3500);
    }

    function stop() {
        if (timer) {
            clearInterval(timer);
            timer = null;
        }
    }

    fetch(`/api/spotlight?type=${type}`)
        .then(res => res.json())
        .then(data => {
            if (!data.length) return;
            items = data;
            render();
            start();
        });

    document.getElementById("spotlightNext")?.addEventListener("click", () => {
        stop(); next(); start();
    });

    document.getElementById("spotlightPrev")?.addEventListener("click", () => {
        stop(); prev(); start();
    });

    // expose pause/resume safely
    window.SpotlightControl = { start, stop };
})();
