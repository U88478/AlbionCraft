document.addEventListener('DOMContentLoaded', function() {
    // Global prices object to store item prices
    const prices = {};

    const searchInput = document.getElementById('search-input');
    const searchResultsDiv = document.getElementById('search-results');
    const contentDiv = document.getElementById('content');
    const popularItemsList = document.getElementById('popular-items-list');

    searchInput.addEventListener('input', function() {
        const query = searchInput.value.trim();
        if (query.length > 2) {
            fetch(`/search?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    searchResultsDiv.innerHTML = ''; // Clear previous results
                    data.items.forEach(item => {
                        const itemElement = document.createElement('div');
                        itemElement.classList.add('search-result-item');
                        itemElement.innerHTML = `
                            <img src="https://render.albiononline.com/v1/item/${item.unique_name}" alt="${item.en_name}">
                            <span>${item.en_name}</span>
                        `;
                        itemElement.addEventListener('click', function() {
                            loadItemDetails(item.unique_name);
                            searchResultsDiv.innerHTML = ''; // Clear results after selection
                        });
                        searchResultsDiv.appendChild(itemElement);
                    });
                });
        } else {
            searchResultsDiv.innerHTML = ''; // Clear results if query is too short
        }
    });

    // Ensure loadItemDetails is in the global scope
    window.loadItemDetails = function(unique_name) {
        fetch(`/item/${unique_name}`)
            .then(response => response.json())
            .then(data => {
                contentDiv.innerHTML = ''; // Clear previous content
                const itemDetails = document.createElement('div');
                itemDetails.classList.add('item-details');
                itemDetails.innerHTML = `
                    <div class="item-container">
                        <div class="similar-items">
                            <h3>Similar Items</h3>
                            <div class="similar-items-grid">
                                ${data.similar_items.map(similarItem => `
                                    <div class="similar-item">
                                        <a href="#" onclick="loadItemDetails('${similarItem.unique_name}')">
                                            <img src="https://render.albiononline.com/v1/item/${similarItem.unique_name}" alt="${similarItem.en_name}">
                                            <p>${similarItem.en_name}</p>
                                        </a>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        <div class="item-main-content">
                            <div class="item-header">
                                <img src="https://render.albiononline.com/v1/item/${data.item.unique_name}" alt="${data.item.en_name}" class="item-image">
                                <div class="item-info">
                                    <h2>${data.item.en_name}</h2>
                                    <p id="item-value">Estimated Market Price: <span id="market-price">loading...</span></p>
                                </div>
                            </div>
                            <div class="section-div">
                                <div class="tab-header">
                                    <div class="tab-title">Details</div>
                                </div>
                                <div class="details-container">
                                    <div id="details" class="tab-content active">
                                        <h3>Details:</h3>
                                        <p>Unique Name: ${data.item.unique_name}</p>
                                        <p>Tier: ${data.item.tier}</p>
                                        <p>Set: ${data.item.set}</p>
                                        <p>Item Power: ${data.item.item_power}</p>
                                        <p>Enchantment Level: ${data.item.enchantment_level}</p>
                                    </div>
                                    <div id="ingredients-list" class="tab-content active">
                                        <h3>Ingredients:</h3>
                                        <ul id="ingredient-list">
                                            ${data.ingredients.map(ingredient => `
                                                <li>${ingredient.quantity} x <img src="https://render.albiononline.com/v1/item/${ingredient.unique_name}" alt="${ingredient.name}" class="ingredient-image"> ${ingredient.name}</li>
                                            `).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div class="section-div">
                                <div id="calculator-header" class="tab-header">
                                    <div class="tab-title">Calculator</div>
                                </div>
                                <div id="calculator">
                                    <div id="calculator-mode">
                                        <div id="regular-mode" class="calculator-content active">
                                            <table id="header-table">
                                                <tr>
                                                    <th>Quantity</th>
                                                    <th>Fame</th>
                                                    <th>Return rate %</th>
                                                </tr>
                                                <tr>
                                                    <td><input type="number" id="craft-quantity" value="1" min="1"></td>
                                                    <td><input type="number" id="fame-per-item" value="0" min="0"></td>
                                                    <td><input type="number" id="return-rate" value="0" min="0" max="100"></td>
                                                </tr>
                                            </table>
                                            <br>
                                            <br>
                                            <br>
                                            <br>
                                            <table id="ingredient-table">
                                                <tr id="ingredient-header">
                                                    <th>Ingredients</th>
                                                    <th>Needed</th>
                                                    <th>Available</th>
                                                    <th>Total</th>
                                                    <th>Total silver</th>
                                                </tr>
                                                ${data.ingredients.map(ingredient => `
                                                    <tr class="ingredient-row" data-ingredient="${ingredient.unique_name}">
                                                        <td>${ingredient.quantity} x <img src="https://render.albiononline.com/v1/item/${ingredient.unique_name}" alt="${ingredient.name}" class="ingredient-image">${ingredient.name}</td>
                                                        <td><input type="number" class="ingredient-quantity" value="${ingredient.quantity}" min="0"></td>
                                                        <td><input type="number" class="ingredient-have" value="0" min="0"></td>
                                                        <td><input type="number" class="ingredient-total" value="0" readonly></td>
                                                        <td><input type="number" class="ingredient-silver" value="0" readonly></td>
                                                    </tr>
                                                `).join('')}
                                                <tr>
                                                    <td class="total-label">Total silver</td>
                                                    <td colspan="2"><input type="number" id="total-silver" readonly></td>
                                                    <td class="profit-label">Profit</td>
                                                    <td><input type="number" id="profit-silver" readonly></td>
                                                </tr>
                                                <tr>
                                                    <td class="total-label">Total fame</td>
                                                    <td colspan="2"><input type="number" id="total-fame" readonly></td>
                                                </tr>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="market-graph">
                                <h3>Market Trends</h3>
                                <div id="market-graphs-container"></div>
                            </div>
                        </div>
                    </div>
                `;
                contentDiv.appendChild(itemDetails);

                // Add event listeners for the calculator inputs
                document.getElementById('craft-quantity').addEventListener('input', updateCalculator);
                document.getElementById('fame-per-item').addEventListener('input', updateCalculator);
                document.getElementById('return-rate').addEventListener('input', updateCalculator);
                document.querySelectorAll('.ingredient-have').forEach(input => {
                    input.addEventListener('input', updateCalculator);
                });

                updateCalculator();

                // Initialize the graph
                fetchItemPrices(unique_name);

                // Fetch the latest price
                fetch(`/item_prices/${unique_name}`)
                    .then(response => response.json())
                    .then(data => {
                        let prices = Object.values(data).flat();
                        if (prices.length > 0) {
                            let latestPrice = prices.reduce((prev, curr) => {
                                return new Date(prev.last_updated) > new Date(curr.last_updated) ? prev : curr;
                            });
                            console.log(latestPrice.price);
                            document.getElementById('market-price').innerText = latestPrice.price;
                        } else {
                            document.getElementById('market-price').innerText = 'No price data';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching item price:', error);
                        document.getElementById('market-price').innerText = 'Error fetching price';
                    });
            });
    }

    function fetchItemPrices(unique_name) {
        fetch(`/item_prices/${unique_name}`)
            .then(response => response.json())
            .then(data => {
                // Store prices in global object
                Object.keys(data).forEach(city => {
                    data[city].forEach(priceData => {
                        prices[priceData.city] = priceData.price;
                    });
                });

                const graphsContainer = document.getElementById('market-graphs-container');
                graphsContainer.innerHTML = ''; // Clear previous graphs

                Object.keys(data).forEach(city => {
                    const cityData = data[city];
                    const canvas = document.createElement('canvas');
                    graphsContainer.appendChild(canvas);

                    const ctx = canvas.getContext('2d');
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: cityData.map(entry => entry.last_updated),
                            datasets: [{
                                label: `${city} Prices`,
                                data: cityData.map(entry => entry.price),
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                x: {
                                    type: 'time',
                                    time: {
                                        unit: 'day'
                                    }
                                },
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                });
            });
    }

    function getItemPrice(unique_name) {
        // Fetch the item price from the global prices object
        return prices[unique_name] || 0;
    }

    function updateCalculator() {
        const quantity = parseInt(document.getElementById('craft-quantity').value, 10);
        const fame = parseInt(document.getElementById('fame-per-item').value, 10);
        const returnRate = parseInt(document.getElementById('return-rate').value, 10);
        const itemValue = parseInt(document.getElementById('market-price').innerText, 10);

        let totalSilver = 0;

        document.querySelectorAll('.ingredient-row').forEach(row => {
            const neededQuantity = parseInt(row.querySelector('.ingredient-quantity').value, 10) * quantity;
            const haveQuantity = parseInt(row.querySelector('.ingredient-have').value, 10);
            const totalRequired = row.querySelector('.ingredient-total');
            const ingredientName = row.dataset.ingredient;

            const returnAmount = Math.floor(neededQuantity * (returnRate / 100));
            const Needed = Math.max(neededQuantity - haveQuantity - returnAmount, 0);
            const silverCost = getItemPrice(ingredientName) * Needed;

            totalRequired.value = Needed;

            const ingredientSilver = row.querySelector('.ingredient-silver');
            if (ingredientSilver) {
                ingredientSilver.value = silverCost;
            }

            totalSilver += silverCost;
        });

        document.getElementById('total-silver').value = totalSilver;
        document.getElementById('total-fame').value = fame * quantity;
        document.getElementById('profit-silver').value = itemValue - totalSilver;
    }

    // Initial load of popular items
    fetch('/popular_items')
        .then(response => response.json())
        .then(data => {
            popularItemsList.innerHTML = data.items.map(item => `
                <div class="popular-item">
                    <a href="#" onclick="loadItemDetails('${item.unique_name}')">
                        <img src="https://render.albiononline.com/v1/item/${item.unique_name}" alt="${item.en_name}">
                        <p>${item.en_name}</p>
                    </a>
                </div>
            `).join('');
        });
});
