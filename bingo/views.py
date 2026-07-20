from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import BingoPlaceholder, Actor
import random
from django.urls import reverse

def play_bingo(request):
    # Only initialize the game if it's not already initialized in the session
    if 'bingo_board' not in request.session or 'bingo_actors' not in request.session:
        # Fetch all placeholders with actors in one optimized query
        placeholders = BingoPlaceholder.objects.prefetch_related('actors').all()
        if len(placeholders) < 16:
            return render(request, 'bingo/error.html', {'message': 'Not enough placeholders in DB (need at least 16).'})

        # Pick 16 random placeholders for the bingo board
        board_placeholders = random.sample(list(placeholders), 16)
        request.session['bingo_board'] = [p.id for p in board_placeholders]

        # Step 1: Fetch actors for placeholders, avoid duplicates
        guaranteed_actors = []
        guaranteed_actor_ids = set()

        for placeholder in board_placeholders:
            actors_for_placeholder = placeholder.actors.all()
            chosen_actor = random.choice(actors_for_placeholder)
            guaranteed_actors.append(chosen_actor)
            guaranteed_actor_ids.add(chosen_actor.id)

        # Step 2: Fill remaining actors (excluding guaranteed ones)
        remaining_needed = 40 - len(guaranteed_actors)
        all_other_actors = Actor.objects.exclude(id__in=guaranteed_actor_ids)
        all_other_actors_list = list(all_other_actors)

        if remaining_needed > len(all_other_actors_list):
            remaining_needed = len(all_other_actors_list)

        additional_actors = random.sample(all_other_actors_list, remaining_needed)

        selected_actors = guaranteed_actors + additional_actors
        random.shuffle(selected_actors)

        # Save selected actors to the session
        request.session['bingo_actors'] = [a.id for a in selected_actors]
        request.session['current_actor_index'] = 0
        request.session['confirmed_placeholders'] = []
        request.session['last_incorrect_id'] = None

    else:
        # Restore board placeholders and actors from the session
        board_ids = request.session.get('bingo_board', [])
        placeholders_qs = BingoPlaceholder.objects.filter(id__in=board_ids).prefetch_related('actors')
        id_to_placeholder = {p.id: p for p in placeholders_qs}
        board_placeholders = [id_to_placeholder[pid] for pid in board_ids if pid in id_to_placeholder]

        actor_ids = request.session.get('bingo_actors')
        if actor_ids is None:
            return redirect('bingo:reset')
        id_to_actor = {actor.id: actor for actor in Actor.objects.filter(id__in=actor_ids)}
        selected_actors = [id_to_actor[aid] for aid in actor_ids if aid in id_to_actor]

    current_index = request.session.get('current_actor_index', 0)
    confirmed_placeholders = request.session.get('confirmed_placeholders', [])

    game_over = False
    game_won = False

    # Check if game over and if player has won
    if current_index >= len(selected_actors):
        current_actor = None
        game_over = True
    else:
        current_actor = selected_actors[current_index]

    if set(confirmed_placeholders) == set(request.session['bingo_board']):
        game_over = True
        game_won = True

    # Always allow retry even if game is over
    if request.method == 'POST' and 'retry' in request.POST:
        # Reset the session when the game is reset
        for key in ['bingo_board', 'bingo_actors', 'current_actor_index', 'confirmed_placeholders', 'last_incorrect_id']:
            if key in request.session:
                del request.session[key]
        return redirect('bingo:play')

    # Group the placeholders into rows for display
    board_rows = [board_placeholders[i:i+4] for i in range(0, 16, 4)]

    # Create the context for rendering the page
    context = {
        'board_rows': board_rows,
        'current_actor': current_actor,
        'current_index': current_index + 1,
        'total_actors': len(selected_actors),
        'confirmed_placeholders': confirmed_placeholders,
        'game_over': game_over,
        'game_won': game_won,
        'last_incorrect_id': request.session.get('last_incorrect_id', None),
    }

    return render(request, 'bingo/play.html', context)

def update_game_state(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        current_index = request.session.get('current_actor_index', 0)
        confirmed_placeholders = request.session.get('confirmed_placeholders', [])
        actor_ids = request.session.get('bingo_actors', [])

        if not actor_ids:
            return JsonResponse({'error': 'No actors found in session'}, status=400)

        # Get current actor
        current_actor = None
        if current_index < len(actor_ids):
            try:
                current_actor = Actor.objects.get(id=actor_ids[current_index])
            except Actor.DoesNotExist:
                current_actor = None

        game_over = False
        game_won = False
        is_correct = None

        if 'skip' in request.POST:
            # Skip to next actor
            current_index += 1
            request.session['current_actor_index'] = current_index
            request.session.modified = True

            # Update current actor after skip
            current_actor = None
            if current_index < len(actor_ids):
                try:
                    current_actor = Actor.objects.get(id=actor_ids[current_index])
                except Actor.DoesNotExist:
                    pass

        elif 'selected_placeholder' in request.POST:
            selected_id = request.POST.get('selected_placeholder')
            is_correct = False

            if selected_id:
                selected_id = int(selected_id)

                if current_actor and current_actor.placeholders.filter(id=selected_id).exists():
                    # Correct match
                    is_correct = True
                    if selected_id not in confirmed_placeholders:
                        confirmed_placeholders.append(selected_id)
                        request.session['confirmed_placeholders'] = confirmed_placeholders
                    current_index += 1
                else:
                    # Incorrect match: apply penalty
                    is_correct = False
                    current_index += 2

                request.session['current_actor_index'] = current_index
                request.session.modified = True

                # Update current actor after selection
                current_actor = None
                if current_index < len(actor_ids):
                    try:
                        current_actor = Actor.objects.get(id=actor_ids[current_index])
                    except Actor.DoesNotExist:
                        pass

        # Check game over conditions
        if current_index >= len(actor_ids):
            game_over = True
            current_actor = None

        if set(confirmed_placeholders) == set(request.session['bingo_board']):
            game_won = True
            game_over = True

        return JsonResponse({
            'current_actor': current_actor.name if current_actor else None,
            'game_over': game_over,
            'game_won': game_won,
            'confirmed_placeholders': confirmed_placeholders,
            'current_index': current_index + 1,
            'total_actors': len(actor_ids),
            'is_correct': is_correct if 'selected_placeholder' in request.POST else None,
        })

    except Exception as e:
        print(f"Error in update_game_state: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def reset_bingo(request):
    for key in ['bingo_board', 'bingo_actors', 'current_actor_index', 'confirmed_placeholders', 'last_incorrect_id']:
        if key in request.session:
            del request.session[key]
    return redirect(reverse('bingo:play'))
