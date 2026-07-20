document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input').forEach(function(input) {
        input.setAttribute('autocomplete', 'off');
    });
});
