document.addEventListener('DOMContentLoaded', function() {
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
                    searchResultsDiv.innerHTML = '';
                    data.items.forEach(item => {
                        const itemElement = document.createElement('div');
                        itemElement.classList.add('search-result-item');
                        itemElement.innerHTML = `
                            <img src="https://render.albiononline.com/v1/item/${item.unique_name}" alt="${item.en_name}">
                            <span>${item.en_name}</span>
                        `;
                        itemElement.addEventListener('click', function() {
                            loadItemDetails(item.unique_name);
                            searchResultsDiv.innerHTML = '';
                        });
                        searchResultsDiv.appendChild(itemElement);
                    });
                });
        } else {
            searchResultsDiv.innerHTML = '';
        }
    });

    window.loadItemDetails = function(unique_name) {
        fetch(`/item/${unique_name}`)
            .then(response => response.json())
            .then(data => {
                contentDiv.innerHTML = '';
                const itemDetails = document.createElement('div');
                itemDetails.classList.add('item-details');
                itemDetails.innerHTML = `
                    <div class="item-container">
                        <div class="similar-items">
                            <h3>Similar Items</h3>
                            <div class="similar-items-grid">
                                ${data.similar_items.map(similarItem => `
                                    <div class="similar-item">
                                        <a class="no-styling-link" href="#" onclick="loadItemDetails('${similarItem.unique_name}'); return false;">
                                            <img src="https://render.albiononline.com/v1/item/${similarItem.unique_name}" alt="${similarItem.en_name}">
                                            <p class="similar-item-text">${similarItem.en_name}</p>
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
                                                    <th>Item Price</th>
                                                </tr>
                                                <tr>
                                                    <td><input type="number" id="craft-quantity" value="1" min="1"></td>
                                                    <td><input type="number" id="fame-per-item" value="0" min="0"></td>
                                                    <td><input type="number" id="return-rate" value="0" min="0" max="100"></td>
                                                    <td><input type="number" id="item-price" value="0" min="0"></td>
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
                                                    <th>Price per unit</th>
                                                    <th>Total silver</th>
                                                </tr>
                                                ${data.ingredients.map(ingredient => `
                                                    <tr class="ingredient-row" data-ingredient="${ingredient.unique_name}">
                                                        <td>${ingredient.quantity} x <img src="https://render.albiononline.com/v1/item/${ingredient.unique_name}" alt="${ingredient.name}" class="ingredient-image"> ${ingredient.name}</td>
                                                        <td><input type="number" class="ingredient-quantity" value="${ingredient.quantity}" min="0"></td>
                                                        <td><input type="number" class="ingredient-have" value="0" min="0"></td>
                                                        <td><input type="number" class="ingredient-total" value="0" readonly></td>
                                                        <td><input type="number" class="ingredient-price" value="0" min="0"></td>
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
                            </div>
                            <div class="market-graph">
                                <h3>Market Trends</h3>
                                <div id="market-graphs-container"></div>
                            </div>
                        </div>
                    </div>
                `;
                contentDiv.appendChild(itemDetails);

                document.getElementById('craft-quantity').addEventListener('input', updateCalculator);
                document.getElementById('fame-per-item').addEventListener('input', updateCalculator);
                document.getElementById('return-rate').addEventListener('input', updateCalculator);
                document.querySelectorAll('.ingredient-have').forEach(input => {
                    input.addEventListener('input', updateCalculator);
                });
                document.querySelectorAll('.ingredient-price').forEach(input => {
                    input.addEventListener('input', updateCalculator);
                });

                fetchIngredientPrices(data.ingredients);

                fetchItemPrices(unique_name);

                updateCalculator();
            });
    }

    function fetchItemPrices(unique_name) {
        fetch(`/item_prices/${unique_name}`)
            .then(response => response.json())
            .then(dbData => {
                if (typeof dbData !== 'object' || Array.isArray(dbData)) {
                    console.error(`Invalid DB response for ${unique_name}:`, dbData);
                    return;
                }
                const apiUrl = `https://west.albion-online-data.com/api/v2/stats/prices/${unique_name}`;
                fetch(apiUrl)
                    .then(apiResponse => apiResponse.json())
                    .then(apiData => {
                        console.log(`API data for ${unique_name}:`, apiData); // Log the API response
                        if (!Array.isArray(apiData)) {
                            console.error(`Invalid API response for ${unique_name}:`, apiData);
                            return;
                        }

                        let combinedData = [];

                        // Flatten the dbData object into an array
                        Object.keys(dbData).forEach(city => {
                            combinedData = combinedData.concat(dbData[city]);
                        });

                        combinedData = combinedData.concat(apiData);

                        let pricesArray = combinedData.filter(price => price.sell_price_min > 0);
                        if (pricesArray.length > 0) {
                            let minPrice = pricesArray.reduce((prev, curr) => {
                                return prev.sell_price_min < curr.sell_price_min ? prev : curr;
                            });
                            document.getElementById('market-price').innerText = minPrice.sell_price_min;
                            document.getElementById('item-price').value = minPrice.sell_price_min;

                            // Save API prices to DB
                            saveApiPricesToDB(unique_name, apiData);
                        } else {
                            document.getElementById('market-price').innerText = 'No price data';
                            document.getElementById('item-price').value = 0;
                        }
                    })
                    .catch(error => {
                        console.error(`Error fetching API price for ${unique_name}:`, error);
                        document.getElementById('market-price').innerText = 'Error fetching price';
                        document.getElementById('item-price').value = 0;
                    });
            })
            .catch(error => {
                console.error('Error fetching DB price:', error);
                document.getElementById('market-price').innerText = 'Error fetching price';
                document.getElementById('item-price').value = 0;
            });
    }

    function fetchIngredientPrices(ingredients) {
        ingredients.forEach(ingredient => {
            fetch(`/item_prices/${ingredient.unique_name}`)
                .then(response => response.json())
                .then(dbData => {
                    if (typeof dbData !== 'object' || Array.isArray(dbData)) {
                        console.error(`Invalid DB response for ${ingredient.unique_name}:`, dbData);
                        return;
                    }
                    const apiUrl = `https://west.albion-online-data.com/api/v2/stats/prices/${ingredient.unique_name}`;
                    fetch(apiUrl)
                        .then(apiResponse => apiResponse.json())
                        .then(apiData => {
                            console.log(`API data for ${ingredient.unique_name}:`, apiData); // Log the API response
                            if (!Array.isArray(apiData)) {
                                console.error(`Invalid API response for ${ingredient.unique_name}:`, apiData);
                                return;
                            }

                            let combinedData = [];

                            // Flatten the dbData object into an array
                            Object.keys(dbData).forEach(city => {
                                combinedData = combinedData.concat(dbData[city]);
                            });

                            combinedData = combinedData.concat(apiData);

                            let pricesArray = combinedData.filter(price => price.sell_price_min > 0);
                            if (pricesArray.length > 0) {
                                let minPrice = pricesArray.reduce((prev, curr) => {
                                    return prev.sell_price_min < curr.sell_price_min ? prev : curr;
                                });
                                document.querySelector(`.ingredient-row[data-ingredient="${ingredient.unique_name}"] .ingredient-price`).value = minPrice.sell_price_min;
                                prices[ingredient.unique_name] = minPrice.sell_price_min;

                                // Save API prices to DB
                                saveApiPricesToDB(ingredient.unique_name, apiData);
                            } else {
                                document.querySelector(`.ingredient-row[data-ingredient="${ingredient.unique_name}"] .ingredient-price`).value = 0;
                                prices[ingredient.unique_name] = 0;
                            }
                            updateCalculator();
                        })
                        .catch(error => {
                            console.error(`Error fetching API price for ${ingredient.unique_name}:`, error);
                            prices[ingredient.unique_name] = 0;
                        });
                })
                .catch(error => {
                    console.error(`Error fetching DB price for ${ingredient.unique_name}:`, error);
                    prices[ingredient.unique_name] = 0;
                });
        });
    }

    function saveApiPricesToDB(unique_name, apiData) {
        apiData.forEach(priceData => {
            if (priceData.sell_price_min > 0) {
                const postData = {
                    unique_name: priceData.item_id,
                    city: priceData.city,
                    price: priceData.sell_price_min
                };
                fetch('/update_price', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(postData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log(`Price for ${unique_name} in ${priceData.city} updated successfully.`);
                    } else {
                        console.error(`Error updating price for ${unique_name} in ${priceData.city}:`, data.error);
                    }
                })
                .catch(error => {
                    console.error(`Error updating price for ${unique_name} in ${priceData.city}:`, error);
                });
            }
        });
    }

    function updateCalculator() {
        const quantity = parseInt(document.getElementById('craft-quantity').value, 10);
        const fame = parseInt(document.getElementById('fame-per-item').value, 10);
        const returnRate = parseInt(document.getElementById('return-rate').value, 10);
        const itemValue = parseInt(document.getElementById('item-price').value, 10);

        let totalSilver = 0;

        document.querySelectorAll('.ingredient-row').forEach(row => {
            const neededQuantity = parseInt(row.querySelector('.ingredient-quantity').value, 10) * quantity;
            const haveQuantity = parseInt(row.querySelector('.ingredient-have').value, 10);
            const UnitPrice = parseInt(row.querySelector('.ingredient-price').value, 10);
            const totalRequired = row.querySelector('.ingredient-total');
            const ingredientName = row.dataset.ingredient;

            const returnAmount = Math.floor(neededQuantity * (returnRate / 100));
            const Needed = Math.max(neededQuantity - haveQuantity - returnAmount, 0);
            const silverCost = UnitPrice * Needed;

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

    fetch('/popular_items')
        .then(response => response.json())
        .then(data => {
            popularItemsList.innerHTML = data.items.map(item => `
                <div class="popular-item">
                    <a class="no-styling-link" href="#" onclick="loadItemDetails('${item.unique_name}'); return false;">
                        <img src="https://render.albiononline.com/v1/item/${item.unique_name}" alt="${item.en_name}">
                        <p class="popular-item-text">${item.en_name}</p>
                    </a>
                </div>
            `).join('');
        });
});
