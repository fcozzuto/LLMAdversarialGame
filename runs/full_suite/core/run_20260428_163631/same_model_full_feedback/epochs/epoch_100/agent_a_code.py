def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    best = None
    best_key = None
    for p in observation.get("resources") or []:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        x, y = int(p[0]), int(p[1])
        if not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles:
            continue
        dx = abs(sx - x)
        dy = abs(sy - y)
        d = dx if dx > dy else dy  # Chebyshev
        # tie-break: prefer smaller d, then smaller x+y, then lexicographic
        key = (d, x + y, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    if best is None:
        return [0, 0]

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    step_x = 0 if sx == tx else (1 if tx > sx else -1)
    step_y = 0 if sy == ty else (1 if ty > sy else -1)

    nx, ny = sx + step_x, sy + step_y
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [step_x, step_y]

    # fallback: try moving in one axis deterministically
    if 0 <= nx < w and (nx, sy) not in obstacles:
        return [step_x, 0]
    if 0 <= ny < h and (sx, ny) not in obstacles:
        return [0, step_y]
    return [0, 0]