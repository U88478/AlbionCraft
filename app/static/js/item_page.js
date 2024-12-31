// Script for populating item details dynamically using preloaded itemData

document.addEventListener("DOMContentLoaded", () => {
    try {
        // Ensure itemData is available
        if (!itemData) {
            console.error("No item data available");
            return;
        }

        // Populate main item details
        document.getElementById("item-name").textContent = itemData.en_name || "Unknown Item";
        document.getElementById("item-value").innerHTML = `Estimated Market Price: <span id="market-price">${itemData.market_price || 'loading...'}</span>`;
        document.getElementById("item-image").src = itemData.icon_url || generateIconUrl(itemData.unique_name);

        // Populate details section
        document.getElementById("item-unique-name").innerHTML = `Unique Name: <span id="span-unique-name">${itemData.unique_name}</span>`;
        document.getElementById("item-tier").textContent = `Tier: ${itemData.tier}`;
        document.getElementById("item-set").textContent = `Set: ${itemData.set}`;
        document.getElementById("item-power").textContent = `Base Item Power: ${itemData.item_power}`;
        document.getElementById("item-enchantment").textContent = `Enchantment Level: ${itemData.enchantment_level}`;

        const span_uname = document.getElementById("span-unique-name");

        span_uname.onclick = function() {
          document.execCommand("copy");
        }

        span_uname.addEventListener("copy", function(event) {
          event.preventDefault();
          if (event.clipboardData) {
            event.clipboardData.setData("text/plain", span_uname.textContent);
          }
        });

        // Populate ingredients
        populateIngredientList(itemData.ingredients);

        // Populate similar items
        populateSimilarItems(itemData.similar_items);

        // Fetch and update prices
        fetchItemPrices(itemData.unique_name);
        updatePricesForIngredients(itemData.ingredients);

        // Populate calculator ingredients
        populateCalculatorIngredients(itemData.ingredients);
    } catch (error) {
        console.error("Error populating item details:", error);
    }
});

function populateIngredientList(ingredients) {
    const ingredientsList = document.getElementById("ingredient-list");
    ingredientsList.innerHTML = ""; // Clear existing content

    if (ingredients && ingredients.length > 0) {
        ingredients.forEach(ingredient => {
            const li = document.createElement("li");
            li.innerHTML = `${ingredient.quantity} x <img src="https://render.albiononline.com/v1/item/${ingredient.unique_name}" alt="${ingredient.name}" class="ingredient-image"> ${ingredient.name}`;
            ingredientsList.appendChild(li);
        });
    } else {
        ingredientsList.innerHTML = "<li>No ingredients found</li>";
    }
}

function populateSimilarItems(similarItems) {
    const similarItemsGrid = document.getElementById("similar-items-grid");
    similarItemsGrid.innerHTML = ""; // Clear existing content

    if (similarItems && similarItems.length > 0) {
        similarItems.forEach(similarItem => {
            const div = document.createElement("div");
            div.classList.add("similar-item");

            div.innerHTML = `
                <a href="/item/${similarItem.unique_name}" class="similar-item-link">
                    <img src="${similarItem.icon_url || generateIconUrl(similarItem.unique_name)}" alt="${similarItem.en_name}" class="similar-item-image">
                    <div class="similar-item-text">${similarItem.en_name}</div>
                </a>
            `;

            similarItemsGrid.appendChild(div);
        });
    } else {
        similarItemsGrid.innerHTML = "<div>No similar items found</div>";
    }
}

function fetchPricesForBridgewatch(pricesArray) {
    // Filter prices for Bridgewatch only
    return pricesArray.filter(price => price.city === "Bridgewatch" && price.sell_price_min > 0);
}

function updatePricesForIngredients(ingredients) {
    ingredients.forEach(ingredient => {
        fetch(`/item_prices/${ingredient.unique_name}`)
            .then(response => response.json())
            .then(dbData => {
                const apiUrl = `https://west.albion-online-data.com/api/v2/stats/prices/${ingredient.unique_name}`;
                fetch(apiUrl)
                    .then(apiResponse => apiResponse.json())
                    .then(apiData => {
                        // Use only Bridgewatch prices
                        const bridgewatchPrices = fetchPricesForBridgewatch(apiData);
                        if (bridgewatchPrices.length > 0) {
                            const minPrice = bridgewatchPrices.reduce((prev, curr) =>
                                prev.sell_price_min < curr.sell_price_min ? prev : curr
                            );
                            const ingredientRow = document.querySelector(`.ingredient-row[data-ingredient="${ingredient.unique_name}"]`);
                            if (ingredientRow) {
                                ingredientRow.querySelector('.ingredient-price').value = minPrice.sell_price_min;
                                updateCalculator();
                            }
                        }
                    })
                    .catch(error => {
                        console.error(`Error fetching API price for ${ingredient.unique_name}:`, error);
                    });
            })
            .catch(error => {
                console.error(`Error fetching DB price for ${ingredient.unique_name}:`, error);
            });
    });
}

function fetchItemPrices(unique_name) {
    fetch(`/item_prices/${unique_name}`)
        .then(response => response.json())
        .then(dbData => {
            const apiUrl = `https://west.albion-online-data.com/api/v2/stats/prices/${unique_name}`;
            fetch(apiUrl)
                .then(apiResponse => apiResponse.json())
                .then(apiData => {
                    // Use only Bridgewatch prices
                    const bridgewatchPrices = fetchPricesForBridgewatch(apiData);
                    if (bridgewatchPrices.length > 0) {
                        const minPrice = bridgewatchPrices.reduce((prev, curr) =>
                            prev.sell_price_min < curr.sell_price_min ? prev : curr
                        );
                        console.log(document.getElementById('item-price'));
                        document.getElementById('market-price').innerText = minPrice.sell_price_min;
                        document.getElementById('item-price').value = minPrice.sell_price_min;
                        updateCalculator();
                    }
                })
                .catch(error => {
                    console.error(`Error fetching API price for ${unique_name}:`, error);
                });
        })
        .catch(error => {
            console.error(`Error fetching DB price for ${unique_name}:`, error);
        });
}

function populateCalculatorIngredients(ingredients) {
    const ingredientTable = document.getElementById('ingredient-table');
    const ingredientHeader = document.getElementById('ingredient-header');

    if (!ingredientTable || !ingredientHeader) {
        console.error("Ingredient table or header not found");
        return;
    }

    // Clear existing ingredient rows
    const existingRows = Array.from(ingredientTable.querySelectorAll('.ingredient-row'));
    existingRows.forEach(row => row.remove());

    // Add ingredients dynamically
    if (ingredients && ingredients.length > 0) {
        ingredients.forEach(ingredient => {
            const row = document.createElement('tr');
            row.classList.add('ingredient-row');
            row.dataset.ingredient = ingredient.unique_name;

            row.innerHTML = `
                <td><img src="https://render.albiononline.com/v1/item/${ingredient.unique_name}.png" alt="${ingredient.name}" class="ingredient-image"> ${ingredient.name}</td>
                <td><input type="number" class="ingredient-quantity" value="${ingredient.quantity}" readonly></td>
                <td><input type="number" class="ingredient-have" value="0" min="0"></td>
                <td><input type="number" class="ingredient-total" value="0" readonly></td>
                <td><input type="number" class="ingredient-price" value="0" min="0"></td>
                <td><input type="number" class="ingredient-silver" value="0" readonly></td>
            `;

            // Safely insert the row after the header
            ingredientHeader.parentNode.insertBefore(row, ingredientHeader.nextSibling);
        });
    } else {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="6">No ingredients found</td>';
        ingredientHeader.parentNode.insertBefore(row, ingredientHeader.nextSibling);
    }

    // Recalculate whenever inputs change
    document.querySelectorAll('.ingredient-have, .ingredient-price').forEach(input => {
        input.addEventListener('input', updateCalculator);
    });
}

function updateCalculator() {
    const quantity = parseInt(document.getElementById('craft-quantity').value, 10) || 1;
    const fame = parseInt(document.getElementById('fame-per-item').value, 10) || 0;
    const returnRate = parseInt(document.getElementById('return-rate').value, 10) || 0;
    const itemPrice = parseInt(document.getElementById('item-price').value, 10) || 0;

    let totalSilver = 0;

    document.querySelectorAll('.ingredient-row').forEach(row => {
        const neededQuantity = parseInt(row.querySelector('.ingredient-quantity').value, 10) * quantity;
        const availableQuantity = parseInt(row.querySelector('.ingredient-have').value, 10) || 0;
        const unitPrice = parseInt(row.querySelector('.ingredient-price').value, 10) || 0;

        const totalNeeded = Math.max(neededQuantity - Math.floor(neededQuantity * returnRate / 100) - availableQuantity, 0);
        const totalCost = totalNeeded * unitPrice;

        row.querySelector('.ingredient-total').value = totalNeeded;
        row.querySelector('.ingredient-silver').value = totalCost;

        totalSilver += totalCost;
    });

    document.getElementById('total-silver').value = totalSilver;
    document.getElementById('total-silver').value = totalSilver;
    document.getElementById('profit-silver').value = itemPrice - totalSilver;
    document.getElementById('total-fame').value = fame * quantity;
}

document.getElementById('craft-quantity').addEventListener('input', updateCalculator);
document.getElementById('fame-per-item').addEventListener('input', updateCalculator);
document.getElementById('return-rate').addEventListener('input', updateCalculator);

document.getElementById('item-price').addEventListener('input', updateCalculator);

function generateIconUrl(uniqueName) {
    const baseUrl = "https://render.albiononline.com/v1/item/";
    return `${baseUrl}${uniqueName}`;
}
