document.addEventListener('DOMContentLoaded', function() {
  var profileIcon = document.getElementById('profile-icon');
  var profileDropdown = document.getElementById('profile-dropdown');

  if (profileIcon && profileDropdown) {
      profileIcon.addEventListener('click', function(e) {
          e.preventDefault();
          profileDropdown.style.display = profileDropdown.style.display === 'block' ? 'none' : 'block';
      });

      // Cerrar el menú si se hace clic fuera de él
      document.addEventListener('click', function(e) {
          if (!profileIcon.contains(e.target) && !profileDropdown.contains(e.target)) {
              profileDropdown.style.display = 'none';
          }
      });
  }
});