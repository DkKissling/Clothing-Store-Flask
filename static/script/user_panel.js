// Función para manejar la eliminación de la fila
function deleteRow(event) {
  event.preventDefault(); // Prevenir el comportamiento por defecto del enlace
  const row = event.target.closest('tr'); // Encontrar la fila más cercana
  if (row) {
      row.remove(); // Eliminar la fila
  }
}

// Función para buscar en la tabla
document.getElementById('search').addEventListener('input', function() {
  const searchTerm = this.value.toLowerCase();
  const rows = document.querySelectorAll('#user-table-body .admin-row');

  rows.forEach(row => {
      const name = row.cells[1].textContent.toLowerCase();
      if (name.includes(searchTerm)) {
          row.style.display = '';
      } else {
          row.style.display = 'none';
      }
  });
});