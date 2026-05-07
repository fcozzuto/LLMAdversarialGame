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
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
    else:
        def dist(a, b):
            ax, ay = a
            bx, by = b
            dx, dy = abs(bx - ax), abs(by - ay)
            return dx if dx > dy else dy  # Chebyshev (diagonal allowed)
        best = None
        best_key = None
        for tx, ty in res:
            sd = dist((sx, sy), (tx, ty))
            od = dist((ox, oy), (tx, ty))
            # Primary: go for resources we can reach no later than opponent; else block with minimal delay.
            # Tie-breakers: advantage, then our distance, then fixed coordinates.
            key = (0 if sd <= od else 1, (od - sd), -sd, tx, ty)  # lexicographic min
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best

    # Choose a safe step that greedily reduces Chebyshev distance to target.
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_md = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        md = max(abs(tx - nx), abs(ty - ny))
        key = (md, abs(ox - nx) + abs(oy - ny), nx, ny)
        if best_md is None or key < best_md:
            best_md = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]