def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        cx, cy = w // 2, h // 2
        tx, ty = (cx, cy)
    else:
        best = None
        best_val = None
        for tx, ty in res:
            sd = abs(sx - tx) + abs(sy - ty)
            od = abs(ox - tx) + abs(oy - ty)
            contested = 1 if sd <= od else 0
            val = (-contested, sd, abs(sx - tx), abs(sy - ty), tx, ty)
            if best_val is None or val < best_val:
                best_val = val
                best = (tx, ty)
        tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        score = (abs(nx - tx) + abs(ny - ty), abs(ox - tx) + abs(oy - ty), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]