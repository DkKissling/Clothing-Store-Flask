document.addEventListener('DOMContentLoaded', function() {
  function updateCartTotals() {
      const cartItems = document.querySelectorAll('#cart-items tr');
      let cartSubtotal = 0;

      cartItems.forEach(row => {
          const priceElement = row.querySelector('.product-price');
          const quantityInput = row.querySelector('.product-quantity');
          const subtotalElement = row.querySelector('[id^="subtotal-"]');

          if (priceElement && quantityInput && subtotalElement) {
              // Remove the currency symbol and convert to float
              const price = parseFloat(priceElement.textContent.replace('₹', '').trim());
              const quantity = parseInt(quantityInput.value);
              
              const subtotal = price * quantity;
              
              // Update subtotal for this row
              subtotalElement.textContent = `₹${subtotal.toFixed(2)}`;
              
              // Add to cart subtotal
              cartSubtotal += subtotal;
          }
      });

      // Update cart subtotal and total
      const cartSubtotalElement = document.getElementById('cart-subtotal');
      const cartTotalElement = document.getElementById('cart-total');
      
      if (cartSubtotalElement && cartTotalElement) {
          cartSubtotalElement.textContent = `₹${cartSubtotal.toFixed(2)}`;
          cartTotalElement.innerHTML = `<strong>₹${cartSubtotal.toFixed(2)}</strong>`;
      }

      // Handle empty cart scenario
      const cartItemsContainer = document.getElementById('cart-items');
      const cartAddSection = document.getElementById('cart-add');
      const cartSection = document.getElementById('cart');

      if (cartItems.length === 0) {
          if (cartAddSection) {
              cartAddSection.remove();
          }
          
          const emptyCartDiv = document.createElement('div');
          emptyCartDiv.id = 'empty-cart';
          emptyCartDiv.innerHTML = `
              <h2>Tu Carrito Está Vacío</h2>
              <p>Parece que aún no has añadido ningún artículo a tu carrito.</p>
              <a href="{{ url_for('product.shop') }}" class="normal">Continuar Comprando</a>
          `;
          cartSection.appendChild(emptyCartDiv);
      }
  }

  function attachRemoveListeners() {
      const removeButtons = document.querySelectorAll('.remove-product');
      
      removeButtons.forEach(button => {
          button.addEventListener('click', function() {
              const productId = this.getAttribute('data-product-id');
              const productRow = document.getElementById(`product-${productId}`);
              
              fetch(`/remove_from_cart/${productId}`, {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                      'X-Requested-With': 'XMLHttpRequest'
                  }
              })
              .then(response => response.json())
              .then(data => {
                  if (data.message) {
                      // Remove the row from the table
                      if (productRow) {
                          productRow.remove();
                      }
                      
                      // Update cart totals
                      updateCartTotals();
                  }
              })
              .catch(error => {
                  console.error('Error:', error);
                  alert('Hubo un problema al eliminar el producto');
              });
          });
      });
  }

  // Initial setup
  updateCartTotals();
  attachRemoveListeners();

  // Update totals when quantity changes
  const quantityInputs = document.querySelectorAll('.product-quantity');
  quantityInputs.forEach(input => {
      input.addEventListener('change', function() {
          const productId = this.getAttribute('data-product-id');
          const newQuantity = parseInt(this.value);

          // Send update to server
          fetch(`/update_cart_quantity/${productId}`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  quantity: newQuantity
              })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  updateCartTotals();
              }
          })
          .catch(error => {
              console.error('Error:', error);
          });
      });
  });
});