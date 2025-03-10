function uploadImage() {
    let formData = new FormData();
    let fileInput = document.getElementById("fileInput");
    let progressBar = document.getElementById("progressBar");

    if (fileInput.files.length === 0) {
        alert("Please select a file!");
        return;
    }

    formData.append("file", fileInput.files[0]);

    // Reset progress bar
    progressBar.style.width = "10%";
    progressBar.innerText = "10%";

    fetch("/api/upload", {
        method: "POST",
        body: formData
    })
    .then(response => {
        progressBar.style.width = "50%";
        progressBar.innerText = "Processing...";
        return response.json();
    })
    .then(data => {
        progressBar.style.width = "100%";
        progressBar.innerText = "Completed!";

        if (data.extracted_text) {
            displayReceiptData(data.extracted_text);
        } else {
            alert("Failed to process image.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        progressBar.style.width = "0%";
        progressBar.innerText = "Error!";
    });
}

function displayReceiptData(receiptData) {
    if (typeof receiptData !== "object" || receiptData === null) {
        alert("Invalid JSON response");
        console.error("Invalid JSON format:", receiptData);
        return;
    }

    document.getElementById("storeName").innerText = receiptData.store_name || "-";
    document.getElementById("receiptDate").innerText = receiptData.date || "-";
    document.getElementById("invoiceCode").innerText = receiptData.invoice_code || "-";

    let productsList = document.getElementById("productsList");
    productsList.innerHTML = "";

    if (Array.isArray(receiptData.products)) {
        receiptData.products.forEach(product => {
            let item = document.createElement("li");
            item.innerText = `🛍️ ${product.name} - €${product.amount.toFixed(2)}`;
            productsList.appendChild(item);
        });
    } else {
        let errorMessage = document.createElement("li");
        errorMessage.innerText = "No products found.";
        productsList.appendChild(errorMessage);
    }

    // Now we compare the selected product with the extracted products
    compareProductWithReceipt(receiptData.products);
}

function compareProductWithReceipt(receiptProducts) {
    const selectedProduct = document.getElementById("productSelect").value;
    const comparisonResultElement = document.getElementById("comparisonResult");

    if (selectedProduct === "0") {
        comparisonResultElement.innerText = "Please select a product to compare.";
        return;
    }

    // Check if the selected product is in the receipt
    const productFound = receiptProducts.some(product => product.name === selectedProduct);

    if (productFound) {
        comparisonResultElement.innerText = `✅ ${selectedProduct} is found in the receipt!`;
    } else {
        comparisonResultElement.innerText = `❌ ${selectedProduct} is NOT found in the receipt.`;
    }
}
