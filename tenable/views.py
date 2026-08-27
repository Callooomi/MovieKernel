from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone
from .models import TenableQuestion, TenableAnswer, MovieTitle, ActorName, normalize_text


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


def guess_suggestions(request, question_id):
    """Small JSON endpoint: returns up to 20 matching titles/names for the
    guess box. Matches against a precomputed, indexed normalized column
    (punctuation/spacing already stripped at save time) rather than
    recomputing that normalization on every row on every keystroke."""
    today = timezone.localdate()
    question = get_object_or_404(TenableQuestion, id=question_id, release_date__lte=today)

    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    normalized_q = normalize_text(q)

    if question.question_type == TenableQuestion.QuestionType.ACTOR:
        results = list(
            ActorName.objects
            .filter(normalized_name__icontains=normalized_q)
            .annotate(
                starts_with_query=Case(
                    When(normalized_name__istartswith=normalized_q, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by('starts_with_query', 'name')
            .values_list('name', flat=True)[:20]
        )
    else:
        results = list(
            MovieTitle.objects
            .filter(normalized_title__icontains=normalized_q)
            .annotate(
                starts_with_query=Case(
                    When(normalized_title__istartswith=normalized_q, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by('starts_with_query', 'title')
            .values_list('title', flat=True)[:20]
        )

    return JsonResponse({'results': results})


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

    # Fetch this puzzle's answers exactly once and reuse the result for
    # everything below — previously this queried the database three
    # separate times per request (once per `question.answers.all()` call).
    answers = list(question.answers.all())
    all_answers = [ans.answer_text for ans in answers]
    all_answers_lower = [text.lower() for text in all_answers]

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

    is_game_over = lives <= 0 or len(correct_guesses) == len(all_answers)

    # Each slot carries whether it's been found, what to display, and — while
    # still unfound — its optional clue.
    ordered_display_answers = []
    for idx, ans in enumerate(answers, start=1):
        found = ans.answer_text.lower() in correct_guesses or reveal or is_game_over
        ordered_display_answers.append({
            'display': ans.answer_text if found else str(idx),
            'found': found,
            'clue': '' if found else ans.clue,
        })

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
        'remaining_lives': lives,
        'message': message,
        'is_game_over': is_game_over,
        'reveal': reveal,
        'all_answers': all_answers,
        'ordered_display_answers': ordered_display_answers,
        'prev_id': prev_id,
        'next_id': next_id,
        'score_summary': score_summary,
        'custom_message': custom_message,
        'incorrect_attempts': incorrect_attempts,
        'question_number': question.id,
    }

    return render(request, 'tenable/play.html', context)