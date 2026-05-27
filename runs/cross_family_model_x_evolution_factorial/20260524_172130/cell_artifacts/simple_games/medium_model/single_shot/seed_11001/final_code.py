def choose_move(observation):
    grid_w = observation.get("grid_width", 0) or 0
    grid_h = observation.get("grid_height", 0) or 0
    pos = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    # simple deterministic heuristic: move toward resource if available, else chase opponent, else stay
    res = observation.get("resources", [])
    best = None
    best_score = -10**9

    # prefer moving toward nearest resource
    if isinstance(res, list) and res:
        for r in res:
            rx, ry, val = r[0], r[1], r[2] if len(r) > 2 else 1
            if not isinstance(rx, int) or not isinstance(ry, int):
                continue
            dx = 0
            dy = 0
            if rx > pos[0]:
                dx = 1
            elif rx < pos[0]:
                dx = -1
            if ry > pos[1]:
                dy = 1
            elif ry < pos[1]:
                dy = -1
            score = - (abs(rx - pos[0]) + abs(ry - pos[1])) + val
            if score > best_score:
                best_score = score
                best = (dx, dy)

    # if no resource guidance, move toward opponent
    if best is None:
        dx = 0
        dy = 0
        if ox > pos[0]:
            dx = 1
        elif ox < pos[0]:
            dx = -1
        if oy > pos[1]:
            dy = 1
        elif oy < pos[1]:
            dy = -1
        best = (dx, dy)

    # clamp to stay within bounds and valid moves
    dx, dy = best
    nx = max(0, min(grid_w - 1, pos[0] + dx))
    ny = max(0, min(grid_h - 1, pos[1] + dy))
    final_dx = nx - pos[0]
    final_dy = ny - pos[1]
    return [final_dx, final_dy]
