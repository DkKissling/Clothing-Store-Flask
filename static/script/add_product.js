let imageCount = 1;  // Iniciar en 1

document.getElementById('product-images').addEventListener('change', function(event) {
  const files = event.target.files;
  const container = document.getElementById('image-preview-container');

  for (let i = 0; i < files.length && imageCount <= 4; i++) {  // Limitar a 4 imágenes
    const file = files[i];
    const reader = new FileReader();

    reader.onload = function(e) {
      const wrapper = document.createElement('div');
      wrapper.className = 'image-preview-wrapper';

      const img = document.createElement('img');
      img.src = e.target.result;
      img.className = 'image-preview';
      wrapper.appendChild(img);

      const input = document.createElement('input');
      input.type = 'file';
      input.name = `product-image-${imageCount}`;  // Comenzar en 1
      input.style.display = 'none';
      input.required = true;
      wrapper.appendChild(input);

      const checkbox = document.createElement('input');
      checkbox.type = 'radio';
      checkbox.name = 'principal-image';
      checkbox.value = imageCount;
      checkbox.className = 'principal-checkbox';
      checkbox.id = `principal-${imageCount}`;
      if (imageCount === 1) checkbox.checked = true;  // La primera imagen es principal
      wrapper.appendChild(checkbox);

      const label = document.createElement('label');
      label.htmlFor = `principal-${imageCount}`;
      label.textContent = 'Principal';
      wrapper.appendChild(label);

      container.appendChild(wrapper);

      // Crear un nuevo objeto File y asignarlo al input oculto
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      input.files = dataTransfer.files;

      imageCount++;
    }

    reader.readAsDataURL(file);
  }

  // Reiniciar el input de archivos
  this.value = '';
});