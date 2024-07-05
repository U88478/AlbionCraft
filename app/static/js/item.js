document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const calculateButton = document.getElementById('calculate-button');
    const craftQuantity = document.getElementById('craft-quantity');
    const calculatedIngredientList = document.getElementById('calculated-ingredient-list');
    const totalCostElement = document.getElementById('total-cost');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(tab.innerText.toLowerCase()).classList.add('active');
        });
    });

    calculateButton.addEventListener('click', () => {
        const quantity = craftQuantity.value;

        fetch('/calculate_craft', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                unique_name: document.querySelector('p:contains("Unique Name:")').innerText.split(': ')[1],
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            calculatedIngredientList.innerHTML = '';
            data.ingredients.forEach(ing => {
                const ingElement = document.createElement('li');
                ingElement.innerHTML = `${ing.quantity} x <img src="https://render.albiononline.com/v1/item/${ing.unique_name}" alt="${ing.name}" class="ingredient-image"> ${ing.name}`;
                calculatedIngredientList.appendChild(ingElement);
            });
            totalCostElement.innerText = data.total_cost;
        });
    });
});
