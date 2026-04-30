def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if resources:
        # Target the nearest resource by Chebyshev distance, deterministic tie-break.
        best = None
        for rx, ry in resources:
            d = max(abs(rx - sx), abs(ry - sy))
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
        cur_to_target = max(abs(tx - sx), abs(ty - sy))

        # Choose move that makes progress toward the target; avoid obstacles.
        best_move = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = max(abs(tx - nx), abs(ty - ny))
            # Secondary: keep away from opponent a bit (deterministic).
            opp_d = max(abs(ox - nx), abs(oy - ny))
            score = (d, -opp_d, nx, ny)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)

        # If fully blocked, fall back to any in-bounds move that reduces distance.
        if best_move is None:
            best_move = (0, 0)
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = max(abs(tx - nx), abs(ty - ny))
                if d < cur_to_target:
                    best_move = (dx, dy)
                    break
        return [best_move[0], best_move[1]]

    # No resources: move toward opponent corner to contest; otherwise drift to center.
    # Deterministic: if opponent is in one of corners, head there; else toward center.
    corners = {(0,0),(0,h-1),(w-1,0),(w-1,h-1)}
    target = (ox, oy) if (ox, oy) in corners else (w//2, h//2)

    tx, ty = target
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = max(abs(tx - nx), abs(ty - ny))
        score = (d, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]