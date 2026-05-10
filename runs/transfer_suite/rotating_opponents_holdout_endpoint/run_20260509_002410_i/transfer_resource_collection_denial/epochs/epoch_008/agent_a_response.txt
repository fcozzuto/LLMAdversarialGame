def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick target with maximum "lead" (opponent distance minus our distance).
    best = None  # (key, tx, ty)
    for rx, ry in resources:
        if (rx, ry) in obstacle_set:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # If equal lead, prefer closer for us; and prefer not too aligned with opponent for denial.
        key = (lead, -ds, -abs((rx - sx) + (ry - sy)), -rx - ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def is_blocked(x, y):
        return (x, y) in obstacle_set or not in_bounds(x, y)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if is_blocked(nx, ny):
                continue
            dist = cheb(nx, ny, tx, ty)
            # Prefer moves that reduce our distance; tie-break deterministically.
            candidates.append((dist, abs(dx) + abs(dy), -dx, -dy, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][4]), int(candidates[0][5])]