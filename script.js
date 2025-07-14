document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const poemList = document.getElementById('poemList');
    const poems = Array.from(poemList.getElementsByTagName('li'));

    function filterAndSort() {
        // --- Filtering (Search) ---
        const searchTerm = searchInput.value.toLowerCase();
        poems.forEach(poem => {
            const title = poem.querySelector('.item-title').textContent.toLowerCase();
            const isVisible = title.includes(searchTerm);
            poem.style.display = isVisible ? 'block' : 'none';
        });

        // --- Sorting ---
        const sortValue = sortSelect.value;
        const sortedPoems = poems.slice().sort((a, b) => {
            const dateA = a.dataset.date;
            const dateB = b.dataset.date;
            if (sortValue === 'newest') {
                return dateB.localeCompare(dateA);
            } else {
                return dateA.localeCompare(dateB);
            }
        });
        
        // Re-append poems to the list in the new order
        sortedPoems.forEach(poem => {
            poemList.appendChild(poem);
        });
    }

    searchInput.addEventListener('input', filterAndSort);
    sortSelect.addEventListener('change', filterAndSort);

    // Initial sort on page load
    filterAndSort();
});