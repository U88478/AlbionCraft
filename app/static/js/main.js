// Main.js

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search-input");
    const searchResults = document.getElementById("search-results");

    const exampleItems = [
        "Adept's Guardian Armor",
        "Expert's Guardian Armor",
        "Master's Guardian Armor",
        "Grandmaster's Guardian Armor",
        "Elder's Guardian Armor",
    ];

    let idleAnimationTimeout;
    let isTyping = false;

    // Typing animation for placeholder
    function startTypingAnimation() {
        let currentItemIndex = 0;
        let currentCharIndex = 0;
        let isErasing = false;

        function animateTyping() {
            if (isTyping) return;
            const currentText = exampleItems[currentItemIndex];

            if (!isErasing) {
                searchInput.placeholder = currentText.slice(0, currentCharIndex++);
                if (currentCharIndex > currentText.length) {
                    isErasing = true;
                    setTimeout(animateTyping, 500);
                } else {
                    setTimeout(animateTyping, 70);
                }
            } else {
                searchInput.placeholder = currentText.slice(0, currentCharIndex--);
                if (currentCharIndex < 0) {
                    isErasing = false;
                    currentItemIndex = (currentItemIndex + 1) % exampleItems.length;
                    setTimeout(animateTyping, 500);
                } else {
                    setTimeout(animateTyping, 30);
                }
            }
        }

        animateTyping();
    }

    startTypingAnimation();

    searchInput.addEventListener("focus", () => {
        isTyping = true;
        clearTimeout(idleAnimationTimeout);
        searchInput.placeholder = "";
    });

    searchInput.addEventListener("blur", () => {
        isTyping = false;
        startTypingAnimation();
    });

    // Search input logic
    searchInput.addEventListener("input", () => {
        const query = searchInput.value.trim();
        if (query.length > 0) {
            fetch(`/search?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = "";
                    if (data.items && data.items.length > 0) {
                        data.items.forEach(item => {
                            const resultDiv = document.createElement("div");
                            resultDiv.classList.add("search-result-item");
                            resultDiv.innerHTML = `
                                <a href="/item/${item.unique_name}" class="result-link">
                                    <img src="https://render.albiononline.com/v1/item/${item.unique_name}" alt="${item.en_name}" class="result-icon">
                                    <div class="search-result-name">${item.en_name}</div>
                                </a>
                                <div class="price-display" style="display: none;">
                                    <span class="price-value"></span>
                                    <img src="https://victorygold.net/images/png/albion/5.png" alt="Silver">
                                </div>
                                <button class="fetch-price-button" data-item="${item.unique_name}">Check Price</button>
                            `;
                            searchResults.appendChild(resultDiv);
                        });
                        searchResults.style.display = "block";
                    } else {
                        searchResults.innerHTML = "<div>No results found</div>";
                        searchResults.style.display = "block";
                    }
                })
                .catch(error => {
                    console.error("Error fetching search results:", error);
                });
        } else {
            searchResults.innerHTML = "";
            searchResults.style.display = "none";
        }
    });

    // Hide results when clicking outside
    document.addEventListener("click", (event) => {
        if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
            searchResults.style.display = "none";
        }
    });

    // Handle "Check Price" button click
    document.addEventListener("click", (event) => {
        if (event.target.classList.contains("fetch-price-button")) {
            event.stopPropagation(); // Prevent the parent link from being triggered
            const itemName = event.target.getAttribute("data-item");
            fetch(`/api/item/${itemName}`)
                .then(response => response.json())
                .then(data => {
                    const parent = event.target.closest(".search-result-item");
                    const priceDisplay = parent.querySelector(".price-display");
                    const priceValue = priceDisplay.querySelector(".price-value");

                    if (data.price) {
                        priceValue.textContent = data.price;
                        priceDisplay.style.display = "flex"; // Show price
                        event.target.remove(); // Remove button
                    } else {
                        priceValue.textContent = "N/A";
                        priceDisplay.style.display = "flex";
                    }
                })
                .catch(error => {
                    console.error("Error fetching price:", error);
                });
        }
    });
});
