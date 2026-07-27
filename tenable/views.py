from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import TenableQuestion, TenableAnswer, MovieTitle, ActorName


def latest_tenable(request):
    """Open the newest puzzle that has been released (by date, then id)."""
    today = timezone.localdate()
    q = (TenableQuestion.objects
         .filter(release_date__lte=today)
         .order_by('-release_date', '-id')
         .first())
    if not q:
        return render(request, 'tenable/empty.html')
    return redirect('tenable:play', question_id=q.id)


def play_tenable(request, question_id):
    today = timezone.localdate()
    # 404 on puzzles that don't exist OR haven't been released yet
    question = get_object_or_404(TenableQuestion, id=question_id, release_date__lte=today)

    # prev/next only walk released puzzles
    all_ids = list(TenableQuestion.objects
                   .filter(release_date__lte=today)
                   .order_by('id')
                   .values_list('id', flat=True))
    current_index = all_ids.index(question_id)

    prev_id = all_ids[current_index - 1] if current_index > 0 else None
    next_id = all_ids[current_index + 1] if current_index < len(all_ids) - 1 else None

    session_correct_key = f'correct_guesses_{question_id}'
    session_lives_key = f'lives_{question_id}'

    correct_guesses = request.session.get(session_correct_key, [])
    lives = request.session.get(session_lives_key, 3)

    message = ''
    reveal = False

    if request.method == 'POST':
        if 'play_again' in request.POST:
            correct_guesses = []
            lives = 3
            reveal = False
            message = "Game restarted! Good luck."
            request.session[session_correct_key] = correct_guesses
            request.session[session_lives_key] = lives

        elif 'reveal' in request.POST:
            reveal = True

        else:
            guess = request.POST.get('guess', '').strip().lower()
            all_answers_lower = [ans.answer_text.lower() for ans in question.answers.all()]

            if guess in all_answers_lower:
                if guess not in correct_guesses:
                    correct_guesses.append(guess)
                    message = f"Correct: {guess.title()}"
                else:
                    message = "Already guessed!"
            else:
                lives -= 1
                message = f"Incorrect. Lives remaining: {lives}"

            request.session[session_correct_key] = correct_guesses
            request.session[session_lives_key] = lives

    all_answers = [ans.answer_text for ans in question.answers.all()]
    is_game_over = lives <= 0 or len(correct_guesses) == len(all_answers)

    # Display format
    ordered_display_answers = []
    for idx, ans in enumerate(question.answers.all(), start=1):
        if ans.answer_text.lower() in correct_guesses or reveal or is_game_over:
            ordered_display_answers.append(ans.answer_text)
        else:
            ordered_display_answers.append(str(idx))

    correct_answers_display = []
    for ans in question.answers.all():
        if ans.answer_text.lower() in correct_guesses:
            correct_answers_display.append(ans.answer_text)

    # Autocomplete source depends on the question's type. Kept the context
    # variable named `movie_titles` (rather than renaming it everywhere) so
    # the template and its JS didn't need any changes at all — it just holds
    # whichever list is appropriate for this particular question.
    if question.question_type == TenableQuestion.QuestionType.ACTOR:
        movie_titles = list(ActorName.objects.values_list('name', flat=True).distinct())
    else:
        movie_titles = list(MovieTitle.objects.values_list('title', flat=True).distinct())

    score_summary = f"{len(correct_guesses)}/{len(all_answers)}"
    incorrect_attempts = 3 - lives

    # Custom message logic
    if len(correct_guesses) == len(all_answers):
        custom_message = "Perfect! You nailed it!"
    elif len(correct_guesses) == len(all_answers) - 1:
        custom_message = "So close! Just one more!"
    elif len(correct_guesses) == 0:
        custom_message = "Give it another go!"
    else:
        custom_message = "Good try!"

    context = {
        'question': question,
        'correct_guesses': correct_guesses,
        'correct_answers_display': correct_answers_display,
        'remaining_lives': lives,
        'message': message,
        'is_game_over': is_game_over,
        'reveal': reveal,
        'all_answers': all_answers,
        'ordered_display_answers': ordered_display_answers,
        'movie_titles': movie_titles,
        'prev_id': prev_id,
        'next_id': next_id,
        'score_summary': score_summary,
        'custom_message': custom_message,
        'incorrect_attempts': incorrect_attempts,
        'question_number': question.id,
    }

    return render(request, 'tenable/play.html', context)