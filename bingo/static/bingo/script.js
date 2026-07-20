document.addEventListener('DOMContentLoaded', function () {
    const gameSection = document.getElementById('game-section');
    if (gameSection) {
        gameSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
