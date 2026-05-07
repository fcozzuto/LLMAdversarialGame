def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
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

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            # try cardinal alternatives deterministically
            candidates = [(dx, 0), (0, dy), (0, 0)]
            for cdx, cdy in candidates:
                nx2, ny2 = sx + cdx, sy + cdy
                if (0 <= nx2 < w and 0 <= ny2 < h) and (nx2, ny2) not in obstacles:
                    return [cdx, cdy]
            return [0, 0]
        return [dx, dy]

    # Prefer resources we can reach no later than opponent; break ties by closer, then by position.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Key: maximize advantage; then minimize our distance; then deterministic ordering.
        key = (do - ds, -ds, -rx, -ry, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    return step_towards(tx, ty)