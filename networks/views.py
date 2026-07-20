import random
from collections import defaultdict
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Board, Tile, Link


def latest(request):
    """Open the newest board that has been released (by date, then id)."""
    today = timezone.localdate()
    board = (Board.objects
             .filter(release_date__lte=today)
             .order_by('-release_date', '-id')
             .first())
    if not board:
        return render(request, 'networks/empty.html')
    return redirect('networks:play', board_id=board.id)


def play_board(request, board_id):
    today = timezone.localdate()
    board = get_object_or_404(Board, id=board_id, release_date__lte=today)

    lives_key = f'board_{board_id}_lives'
    lives = request.session.get(lives_key, 3)

    solved_paths = request.session.get(f'board_{board_id}_solved_paths', [])
    locked_tile_ids = {}
    for i, path in enumerate(solved_paths):
        color_class = f'locked-{min(i + 1, 6)}'
        for tile_id in path:
            locked_tile_ids[int(tile_id)] = color_class

    tiles_by_column = {}
    for i in range(1, 6):
        column_tiles = [tile for tile in board.tiles.all() if tile.column == i]
        locked = []
        unlocked = []
        for tile in column_tiles:
            if tile.id in locked_tile_ids:
                locked.append((tile, locked_tile_ids[tile.id]))
            else:
                unlocked.append(tile)
        random.shuffle(unlocked)
        locked.sort(key=lambda pair: int(pair[1].split('-')[1]))
        tiles_by_column[i] = [tile for tile, _ in locked] + unlocked

    all_board_ids = list(Board.objects.filter(release_date__lte=today)
                         .values_list('id', flat=True).order_by('id'))
    current_index = all_board_ids.index(board.id)
    prev_board_id = all_board_ids[current_index - 1] if current_index > 0 else None
    next_board_id = all_board_ids[current_index + 1] if current_index < len(all_board_ids) - 1 else None

    context = {
        'board': board,
        'tiles_by_column': [tiles_by_column[i] for i in range(1, 6)],
        'lives': lives,
        'prev_board_id': prev_board_id,
        'next_board_id': next_board_id,
        'locked_tile_ids': locked_tile_ids,
        'game_over': lives <= 0 or len(solved_paths) >= 6,
        'solved_count': len(solved_paths),
    }
    return render(request, 'networks/play.html', context)

def submit_path(request, board_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    tile_ids = request.POST.getlist('tile_ids')
    if len(tile_ids) != 5:
        return JsonResponse({'success': False, 'message': 'Select one tile from each column.'})

    board = get_object_or_404(Board, id=board_id)
    valid = True
    for i in range(4):
        from_id = tile_ids[i]
        to_id = tile_ids[i + 1]
        if not Link.objects.filter(board=board, from_tile_id=from_id, to_tile_id=to_id).exists():
            valid = False
            break

    lives_key = f'board_{board_id}_lives'
    solved_key = f'board_{board_id}_solved_paths'

    lives = request.session.get(lives_key, 3)
    solved_paths = request.session.get(solved_key, [])

    if valid:
        solved_paths.append(tile_ids)
        request.session[solved_key] = solved_paths
        return JsonResponse({'success': True, 'message': 'Correct path!'})
    else:
        lives = max(lives - 1, 0)
        request.session[lives_key] = lives
        return JsonResponse({'success': False, 'message': f'Incorrect. {lives} lives remaining.', 'lives': lives})

def reveal_answers(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    links = Link.objects.filter(board=board)
    graph = defaultdict(list)
    for link in links:
        graph[link.from_tile_id].append(link.to_tile_id)

    def dfs(path):
        if len(path) == 5:
            all_paths.append(path[:])
            return
        for next_id in graph.get(path[-1], []):
            if next_id not in path:
                dfs(path + [next_id])

    all_paths = []
    start_tiles = Tile.objects.filter(board=board, column=1)
    for tile in start_tiles:
        dfs([tile.id])

    solved = request.session.get(f'board_{board_id}_solved_paths', [])
    solved_set = set(tuple(p) for p in solved)

    unsolved_paths = [p for p in all_paths if tuple(p) not in solved_set]
    unsolved_paths = unsolved_paths[:6]

    return JsonResponse({'paths': unsolved_paths})


def reset_lives(request, board_id):
    request.session[f'board_{board_id}_lives'] = 3
    request.session[f'board_{board_id}_solved_paths'] = []
    return redirect('networks:play', board_id=board_id)
