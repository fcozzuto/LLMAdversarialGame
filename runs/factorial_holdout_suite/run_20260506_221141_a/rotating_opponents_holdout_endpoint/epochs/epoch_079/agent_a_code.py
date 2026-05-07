def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # chebyshev for diagonal moves

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, None)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles and (dx, dy) != (0, 0):
            continue

        # Evaluate move by best resource we could reach soonest, while opponent lags.
        # Deterministic tie-breaking with consistent ordering.
        local_best_self = None
        local_best_key = None
        for r in resources:
            ds = dist((nx, ny), r)
            do = dist((ox, oy), r)
            # primary: advantage = opponent_time - self_time
            key = (do - ds, -ds, r[0], r[1])
            if local_best_key is None or key > local_best_key:
                local_best_key = key
                local_best_self = ds

        # Global choice across moves: prefer higher advantage, then closer, then smaller dx/dy index.
        # Since resources tie-break includes r coords, move tie-break stays deterministic.
        if local_best_key is None:
            continue
        global_key = (local_best_key[0], local_best_key[1], dx, dy)
        if best_key is None or global_key > best_key:
            best_key = global_key
            best = (dx, dy)

    if best[0] is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]