import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Actor

def _normalize_stat(stat: str | None) -> str:
    """Map old stat names to new ones for backward compatibility."""
    if not stat:
        return 'age'
    if stat == 'acting_credits':
        return 'leading_roles'
    return stat

def higher_or_lower(request):
    # Handle AJAX requests for animations
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return handle_guess_ajax(request)

    # Handle play again functionality
    if request.method == 'POST' and 'play_again' in request.POST:
        # Clear all game-related session data
        request.session.pop('current_actor', None)
        request.session.pop('game_over', None)
        request.session.pop('score', None)
        request.session.pop('current_stat', None)
        request.session.pop('right_actor', None)     # Clear locked-in right actor
        request.session.pop('previous_actor', None)  # Clear previous actor tracking
        return redirect('higherorlower:higher_or_lower')

    # Initialize game session if not already present
    if 'current_actor' not in request.session or request.session.get('game_over', False):
        # Check if we have actors in the database
        if Actor.objects.count() < 3:  # Need at least 3 actors now to avoid repeats
            return render(request, 'higherorlower/game.html', {
                'error': 'Not enough actors in database. Please add at least 3 actors.',
                'game_over': True
            })

        current_actor = random.choice(Actor.objects.all())
        request.session['current_actor'] = current_actor.id
        request.session['game_over'] = False
        request.session['score'] = 0
        request.session['previous_actor'] = None  # No previous actor at game start

        # Pick a random stat for the first round (use the NEW field name)
        stat_choices = ['age', 'box_office', 'leading_roles', 'oscar_nominations']
        request.session['current_stat'] = random.choice(stat_choices)

        # Initialize right actor as None - will be set below
        request.session['right_actor'] = None

    # Get current actor from session
    try:
        current_actor = Actor.objects.get(id=request.session['current_actor'])
    except Actor.DoesNotExist:
        # If actor doesn't exist, restart the game
        return redirect('higherorlower:higher_or_lower')

    # Get all other actors (excluding current one and previous one)
    excluded_ids = [current_actor.id]
    if request.session.get('previous_actor'):
        excluded_ids.append(request.session['previous_actor'])

    other_actors = Actor.objects.exclude(id__in=excluded_ids)
    if not other_actors.exists():
        # Fallback: if no actors available (shouldn't happen with 3+ actors), just exclude current
        other_actors = Actor.objects.exclude(id=current_actor.id)
        if not other_actors.exists():
            return render(request, 'higherorlower/game.html', {
                'error': 'Not enough actors in database. Please add more actors.',
                'game_over': True
            })

    # Check if we already have a locked-in right actor for this round
    if request.session.get('right_actor'):
        try:
            right_actor = Actor.objects.get(id=request.session['right_actor'])
            # Verify this actor is still valid (not the current actor or previous actor)
            if right_actor.id in excluded_ids:
                # If the stored right actor is now excluded, pick a new one
                right_actor = random.choice(other_actors)
                request.session['right_actor'] = right_actor.id
        except Actor.DoesNotExist:
            # If the stored right actor doesn't exist, pick a new one
            right_actor = random.choice(other_actors)
            request.session['right_actor'] = right_actor.id
    else:
        # No right actor set yet, pick a new one and lock it in
        right_actor = random.choice(other_actors)
        request.session['right_actor'] = right_actor.id

    print(f"DEBUG: Current actor: {current_actor.name} (ID: {current_actor.id})")
    print(f"DEBUG: Previous actor ID: {request.session.get('previous_actor', 'None')}")
    print(f"DEBUG: Excluded IDs: {excluded_ids}")
    print(f"DEBUG: Locked-in right actor: {right_actor.name} (ID: {right_actor.id})")

    # Get current stat from session (normalize old value if present)
    current_stat = _normalize_stat(request.session.get('current_stat', 'age'))
    # Write back the normalized value so future requests are clean
    request.session['current_stat'] = current_stat

    # Create display name for the stat
    stat_display_names = {
        'age': 'Age',
        'box_office': 'Box Office ($ millions)',
        'leading_roles': 'Leading Roles',
        'oscar_nominations': 'Oscar Nominations'
    }
    left_stat_name = stat_display_names.get(current_stat, current_stat.replace('_', ' ').title())

    message = ''

    # Check for success message from previous round
    if 'success_message' in request.session:
        message = request.session.pop('success_message')

    # Get the current stat value for display
    left_stat_value = getattr(current_actor, current_stat)

    # Determine side colors based on score
    current_score = request.session.get('score', 0)
    left_side_red = (current_score % 2 == 0)  # Even scores = red left, odd scores = black left

    print(f"DEBUG: Current score = {current_score}")
    print(f"DEBUG: left_side_red = {left_side_red}")

    context = {
        'current_actor': current_actor,
        'right_actor': right_actor,
        'left_stat_name': left_stat_name,
        'left_stat_value': left_stat_value,
        'current_stat': current_stat,
        'game_over': request.session.get('game_over', False),
        'message': message,
        'score': current_score,
        'left_side_red': left_side_red,  # Pass color info to template
    }

    return render(request, 'higherorlower/game.html', context)

def handle_guess_ajax(request):
    """Handle AJAX requests for guess processing"""
    guess = request.POST.get('guess')

    # Get the exact actors that were displayed to the user
    displayed_right_actor_id = request.POST.get('right_actor_id')
    displayed_current_stat = _normalize_stat(request.POST.get('current_stat'))

    print(f"DEBUG: Guess = {guess}")
    print(f"DEBUG: Right actor ID = {displayed_right_actor_id}")
    print(f"DEBUG: Current stat (normalized) = {displayed_current_stat}")

    if not displayed_right_actor_id or not displayed_current_stat:
        return JsonResponse({'error': 'Missing required data'}, status=400)

    try:
        # Get current actor from session
        current_actor = Actor.objects.get(id=request.session['current_actor'])
        displayed_right_actor = Actor.objects.get(id=displayed_right_actor_id)

        print(f"DEBUG: Current actor = {current_actor.name}")
        print(f"DEBUG: Right actor = {displayed_right_actor.name}")

        # Get stat values for comparison using the displayed actors and stat
        left_stat_value = getattr(current_actor, displayed_current_stat)
        right_stat_value = getattr(displayed_right_actor, displayed_current_stat)

        print(f"DEBUG: Left stat value = {left_stat_value}")
        print(f"DEBUG: Right stat value = {right_stat_value}")
        print(f"DEBUG: Stat being compared = {displayed_current_stat}")

        # Determine if guess is correct
        is_correct = False

        if left_stat_value == right_stat_value:
            # If values are the same, user gets a point regardless of guess
            is_correct = True
            message = f"Values are the same ({right_stat_value})! You get a point!"
            print("DEBUG: Values are the same - correct!")
        elif guess == 'higher':
            is_correct = right_stat_value > left_stat_value
            if is_correct:
                message = f"Correct! {displayed_right_actor.name} has {right_stat_value} (higher than {left_stat_value})"
                print("DEBUG: Higher guess - correct!")
            else:
                message = f"Wrong! {displayed_right_actor.name} has {right_stat_value} (lower than {left_stat_value})"
                print("DEBUG: Higher guess - wrong!")
        elif guess == 'lower':
            is_correct = right_stat_value < left_stat_value
            if is_correct:
                message = f"Correct! {displayed_right_actor.name} has {right_stat_value} (lower than {left_stat_value})"
                print("DEBUG: Lower guess - correct!")
            else:
                message = f"Wrong! {displayed_right_actor.name} has {right_stat_value} (higher than {left_stat_value})"
                print("DEBUG: Lower guess - wrong!")

        print(f"DEBUG: Final is_correct = {is_correct}")

        if is_correct:
            # Correct guess: Update score and make the right actor the new current actor
            request.session['score'] = request.session.get('score', 0) + 1

            # Store the current actor as the previous actor before updating
            request.session['previous_actor'] = current_actor.id

            # The right actor (the one we just guessed about) becomes the new current actor
            request.session['current_actor'] = displayed_right_actor.id

            # Clear the right actor so a new one will be chosen for the next round
            request.session['right_actor'] = None

            print(f"DEBUG: Score updated to {request.session['score']}")
            print(f"DEBUG: Previous actor set to: {current_actor.name} (ID: {current_actor.id})")
            print(f"DEBUG: New current actor: {displayed_right_actor.name} (ID: {displayed_right_actor.id})")
            print(f"DEBUG: Cleared right actor - new one will be chosen next round")

            # Pick a new random stat for the next round (use NEW names)
            stat_choices = ['age', 'box_office', 'leading_roles', 'oscar_nominations']
            current_stat = _normalize_stat(request.session.get('current_stat', 'age'))
            new_stat = random.choice(stat_choices)
            while new_stat == current_stat:  # Ensure new stat is different from the current one
                new_stat = random.choice(stat_choices)
            request.session['current_stat'] = new_stat

            return JsonResponse({
                'correct': True,
                'message': message,
                'right_stat_value': right_stat_value,
                'redirect_url': '/higherorlower/'  # Adjust this to your actual URL
            })
        else:
            # Incorrect guess: End the game
            request.session['game_over'] = True
            final_score = request.session.get('score', 0)
            message = f"Game Over! Final score: {final_score}"

            return JsonResponse({
                'correct': False,
                'message': message,
                'right_stat_value': right_stat_value,
                'game_over': True,
                'final_score': final_score
            })

    except Actor.DoesNotExist:
        print("DEBUG: Actor not found!")
        return JsonResponse({'error': 'Actor not found'}, status=404)
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        return JsonResponse({'error': str(e)}, status=500)
