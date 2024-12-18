function toggleStock(productId) {
  fetch(`/toggle_stock/${productId}`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          const button = document.querySelector(`#stock-button-${productId}`);
          button.textContent = data.message;
          button.classList.toggle('in-stock');
          button.classList.toggle('out-of-stock');
      } else {
          alert('Error al cambiar el estado del stock');
      }
  })
  .catch(error => {
      console.error('Error:', error);
      alert('Error al cambiar el estado del stock');
  });
}