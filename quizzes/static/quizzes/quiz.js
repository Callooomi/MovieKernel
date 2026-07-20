(function () {
  // ---- Multiple choice: click to lock, colour, and tally a score ----
  var scoreEl = document.getElementById('quiz-score');
  var scoreText = document.getElementById('quiz-score-text');
  var total = scoreEl ? parseInt(scoreEl.dataset.total, 10) : 0;
  var answered = 0;
  var correct = 0;

  function updateScore() {
    if (!scoreText) return;
    if (answered < total) {
      scoreText.textContent = 'Answered ' + answered + ' / ' + total +
        '  ·  Score ' + correct;
    } else {
      scoreText.textContent = 'Final score: ' + correct + ' / ' + total;
    }
  }

  document.querySelectorAll('[data-choices]').forEach(function (group) {
    var buttons = group.querySelectorAll('.mk-choice');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (group.classList.contains('answered')) return;  // lock after first pick
        group.classList.add('answered');

        var isCorrect = btn.dataset.correct === '1';
        if (isCorrect) {
          btn.classList.add('correct');
          correct += 1;
        } else {
          btn.classList.add('incorrect');
          // also light up the right answer so they learn it
          buttons.forEach(function (b) {
            if (b.dataset.correct === '1') b.classList.add('correct');
          });
        }
        buttons.forEach(function (b) { b.classList.add('answered-set'); });
        answered += 1;
        updateScore();
      });
    });
  });

  // ---- Click to reveal ----
  document.querySelectorAll('[data-reveal-btn]').forEach(function (btn) {
    var answer = btn.parentElement.querySelector('[data-reveal-answer]');
    btn.addEventListener('click', function () {
      if (!answer) return;
      var hidden = answer.hasAttribute('hidden');
      if (hidden) {
        answer.removeAttribute('hidden');
        btn.textContent = 'Hide answer';
      } else {
        answer.setAttribute('hidden', '');
        btn.textContent = 'Reveal answer';
      }
    });
  });
})();
