def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a target: nearest resource if present, else toward center, otherwise away from opponent when close.
    resources = observation.get("resources", None)
    if resources and isinstance(resources, list) and resources:
        best = None
        for p in resources:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                x, y = int(p[0]), int(p[1])
                d = abs(x - sx) + abs(y - sy)
                if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
                    best = (d, (x, y))
        tx, ty = best[1] if best else (w // 2, h // 2)
    else:
        tx, ty = w // 2, h // 2

    # If opponent is very close, bias away.
    oppd = abs(ox - sx) + abs(oy - sy)
    if oppd <= 2:
        tx = sx - (1 if ox >= sx else -1)
        ty = sy - (1 if oy >= sy else -1)

    tx = max(0, min(w - 1, int(tx)))
    ty = max(0, min(h - 1, int(ty)))

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_target = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        # Higher is better: prefer closer to target, farther from opponent.
        score = (d_target * -10) + d_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]