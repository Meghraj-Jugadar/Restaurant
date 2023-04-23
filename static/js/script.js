function clearMessage() {
    document.getElementById("name").innerHTML = "";
    document.getElementById("number").innerHTML = "";
}
function add(row) {
    var name = row.cells[1].textContent;
    var price = row.cells[2].textContent;
    document.getElementById('food_name').value = name;
    document.getElementById('food_price').value = price;
}
function calculateTotal() {
    var subtotals = document.getElementsByClassName("subtotal");
    var total = 0;
    for (var i = 0; i < subtotals.length; i++) {
        total += parseFloat(subtotals[i].innerText);
    }
    document.getElementById("total").value = total;
}

function calculateSubtotal(input) {
    const price = input.parentElement.parentElement.querySelector('#price').value;
    const quantity = input.value;
    const subtotal = price * quantity;
    input.parentElement.parentElement.querySelector('#subtotal').value = subtotal;
}
