document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const tierFilter = document.getElementById('tier-filter');
    const enchFilter = document.getElementById('ench-filter');
    const craftingPageButton = document.getElementById('crafting-page-button');

    let selectedItemUniqueName = '';

    searchInput.addEventListener('input', function() {
        const query = searchInput.value;
        if (query.length > 2) {
            fetch(`/search?query=${query}&tier=${tierFilter.value}&ench=${enchFilter.value}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = '';
                    data.items.forEach(item => {
                        const itemElement = document.createElement('div');
                        itemElement.className = 'search-result-item';
                        itemElement.innerHTML = `
                            <img src="https://render.albiononline.com/v1/item/${item.unique_name}" alt="${item.en_name}">
                            <span>${item.en_name}</span>
                        `;
                        itemElement.addEventListener('click', function() {
                            searchInput.value = item.en_name;
                            selectedItemUniqueName = item.unique_name;
                            searchResults.style.display = 'none';
                        });
                        searchResults.appendChild(itemElement);
                    });
                    searchResults.style.display = 'block';
                });
        } else {
            searchResults.style.display = 'none';
        }
    });

    craftingPageButton.addEventListener('click', function() {
        if (selectedItemUniqueName) {
            window.location.href = `/item/${selectedItemUniqueName}`;
        } else {
            alert('Please select an item from the search results.');
        }
    });
});
