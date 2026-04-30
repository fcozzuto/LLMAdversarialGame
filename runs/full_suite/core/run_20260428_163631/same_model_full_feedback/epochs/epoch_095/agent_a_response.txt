def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Deterministic: pick resource with best (reach advantage, proximity, tie breaks)
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Encourage winning races first; then reduce our distance; then move toward center-ish.
        race = ds - do  # lower is better
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        # Tie-break deterministically using coordinates to avoid oscillation.
        key = (race, ds, center_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose move that reduces distance to target and is not blocked/out of bounds.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference: closer distance first, then lexicographic delta.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dnext = cheb(nx, ny, tx, ty)
            candidates.append((dnext, dx, dy))
    # If somehow no candidates (unlikely), stay.
    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][1]), int(candidates[0][2])]