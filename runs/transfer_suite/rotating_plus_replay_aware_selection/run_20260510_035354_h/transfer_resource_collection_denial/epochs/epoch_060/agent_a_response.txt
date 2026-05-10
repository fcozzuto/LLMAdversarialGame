def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    def chebd(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for rx, ry in res:
        sd = chebd((sx, sy), (rx, ry))
        od = chebd((ox, oy), (rx, ry))
        # Primary: resources where we are closer than opponent (larger od - sd).
        # Secondary: closer to target.
        score = (od - sd, -sd, -rx, -ry)
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_m = (0, 0)
    best_ms = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d2 = chebd((nx, ny), (tx, ty))
        # Prefer stepping closer; slight bias to avoid letting opponent take it next.
        od2 = chebd((ox, oy), (tx, ty))
        # Also encourage moving toward a resource even if far: smaller d2 better.
        ms = (-d2, -(od2 - d2), -nx, -ny)
        if best_ms is None or ms > best_ms:
            best_ms = ms
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]