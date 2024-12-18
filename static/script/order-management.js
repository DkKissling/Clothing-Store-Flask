document.getElementById('orderForm').addEventListener('submit', function(event) {
  event.preventDefault();

  const customerName = document.getElementById('customerName').value;
  const orderItem = document.getElementById('orderItem').value;
  const orderQuantity = document.getElementById('orderQuantity').value;

const tableBody = document.getElementById('orderTableBody');
const newRow = document.createElement('tr');

  newRow.innerHTML = `
      <td data-label="Cliente">${customerName}</td>
      <td data-label="Artículo">${orderItem}</td>
      <td data-label="Cantidad">${orderQuantity}</td>
      <td data-label="Estado">
          <select class="status-select status-pendiente" onchange="updateOrderStatus(this)">
              <option value="Pendiente" class="status-pendiente">Pendiente</option>
              <option value="En Proceso" class="status-en-proceso">En Proceso</option>
              <option value="Completado" class="status-completado">Completado</option>
              <option value="Cancelado" class="status-cancelado">Cancelado</option>
          </select>
      </td>
  `;

  tableBody.appendChild(newRow);
  document.getElementById('orderForm').reset();
});

function updateOrderStatus(selectElement) {
  const newStatus = selectElement.value;
  selectElement.className = 'status-select status-' + newStatus.toLowerCase().replace(' ', '-');
}

function generateList(status) {
  const orders = document.querySelectorAll('#orderTableBody tr');
  let listHTML = `<h3>Pedidos ${status}</h3><ul>`;

  orders.forEach(order => {
      const orderStatus = order.querySelector('select').value;
      if (orderStatus === status) {
          const customerName = order.children[0].textContent;
          const orderItem = order.children[1].textContent;
          const orderQuantity = order.children[2].textContent;
          listHTML += `<li>${customerName} - ${orderItem} - Cantidad: ${orderQuantity}</li>`;
      }
  });

  listHTML += '</ul>';
  document.getElementById('orderList').innerHTML = listHTML;
}

function generateFullReport() {
  const orders = document.querySelectorAll('#orderTableBody tr');
  const statuses = ['Pendiente', 'En Proceso', 'Completado', 'Cancelado'];
  let reportHTML = '';
  let totalProducts = 0;

  statuses.forEach(status => {
      let count = 0;
      let totalQuantity = 0;
      let itemsHTML = '<ul>';
      
      orders.forEach(order => {
          const orderStatus = order.querySelector('select').value;
          if (orderStatus === status) {
              const customerName = order.children[0].textContent;
              const orderItem = order.children[1].textContent;
              const orderQuantity = parseInt(order.children[2].textContent);
              itemsHTML += `<li>${customerName} - ${orderItem} - Cantidad: ${orderQuantity}</li>`;
              count++;
              totalQuantity += orderQuantity;
          }
      });

      itemsHTML += '</ul>';

      if (count > 0) {
          reportHTML += `<h3>${status} (${count} pedidos, ${totalQuantity} productos)</h3>${itemsHTML}`;
          totalProducts += totalQuantity;
      }
  });

  reportHTML += `<h3>Total de productos vendidos: ${totalProducts}</h3>`;
  document.getElementById('orderList').innerHTML = reportHTML;
}