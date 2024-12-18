function handleAddToCart(productId) {
  {% if session.get('user_id') %}
      // Si está autenticado, enviar al carrito
      var form = document.getElementById('add-to-cart-form');
      var formData = new FormData(form);
      
      fetch("{{ url_for('product.add_to_cart', product_id=producto.producto_id) }}", {
          method: 'POST',
          body: formData
      })
      .then(response => {
          if (response.ok) {
              window.location.href = "{{ url_for('product.cart') }}";
          } else {
              alert('Error al añadir al carrito');
          }
      })
      .catch(error => {
          console.error('Error:', error);
          alert('Error al añadir al carrito');
      });
  {% else %}
      // Si no está autenticado, redirigir al login
      window.location.href = "{{ url_for('auth.login') }}";
  {% endif %}
}
function changeMainImage(smallImg) {
  var mainImg = document.getElementById("MainImg");
  mainImg.src = smallImg.src;
}