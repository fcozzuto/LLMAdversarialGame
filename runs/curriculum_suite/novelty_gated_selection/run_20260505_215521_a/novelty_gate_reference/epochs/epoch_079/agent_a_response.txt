def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose best resource we can contest (arrive no later than opponent).
        # Deterministic tie-break uses move order and lexicographic resource effects.
        local_best = None
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            contest = d2 - d1  # positive means we arrive earlier
            # Prefer: (contest high), then (our distance low), then (opponent distance high)
            key = (contest, -d1, d2, rx, ry)
            if local_best is None or key > local_best[0]:
                local_best = (key, rx, ry)
        if local_best is None:
            continue

        # Encourage moves that improve overall reach vs opponent near these best targets.
        top_key = local_best[0]
        # Secondary tie-break: prefer staying closer to board center deterministically.
        center = max(w, h) // 2
        center_bias = - (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        overall = (top_key[0], top_key[1], top_key[2], center_bias, dx, dy)
        if best is None or overall > best[0]:
            best = (overall, dx, dy)

    return [int(best[1]), int(best[2])] if best else [0, 0]