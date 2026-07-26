(function () {
  // ---- Shared score tracking (used by both quiz types) ----
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

  // ---- Multiple choice: click to lock, colour, and tally a score ----
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

  // ---- Click to reveal, with self-marked scoring ----
  document.querySelectorAll('[data-reveal-btn]').forEach(function (btn) {
    var wrapper = btn.parentElement;
    var answer = wrapper.querySelector('[data-reveal-answer]');
    var scoreRow = wrapper.querySelector('[data-reveal-score]');

    btn.addEventListener('click', function () {
      if (!answer) return;
      var hidden = answer.hasAttribute('hidden');
      if (hidden) {
        answer.removeAttribute('hidden');
        btn.textContent = 'Hide answer';
        // reveal the yes/no prompt too, unless this question's already been marked
        if (scoreRow && !scoreRow.dataset.marked) {
          scoreRow.removeAttribute('hidden');
        }
      } else {
        answer.setAttribute('hidden', '');
        btn.textContent = 'Reveal answer';
      }
    });

    if (scoreRow) {
      scoreRow.querySelectorAll('[data-reveal-correct]').forEach(function (markBtn) {
        markBtn.addEventListener('click', function () {
          if (scoreRow.dataset.marked) return;  // lock after first pick
          scoreRow.dataset.marked = '1';

          var wasCorrect = markBtn.dataset.revealCorrect === '1';
          markBtn.classList.add('picked');
          if (wasCorrect) correct += 1;
          answered += 1;
          updateScore();
        });
      });
    }
  });
})();