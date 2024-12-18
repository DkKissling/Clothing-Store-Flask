    function togglePasswordVisibility(inputId) {
        var input = document.getElementById(inputId);
        var type = input.type === 'password' ? 'text' : 'password';
        input.type = type;
    }