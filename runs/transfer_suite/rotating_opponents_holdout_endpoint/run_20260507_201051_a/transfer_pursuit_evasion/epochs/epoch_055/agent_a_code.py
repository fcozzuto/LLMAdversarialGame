def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    w = int(w) if w is not None else 8
    h = int(h) if h is not None else 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) in obs:
        obs.discard((sx, sy))

    def dist_metric(nx, ny):
        # prioritize reaching exact cell; otherwise minimize Chebyshev distance
        dx, dy = nx - ox, ny - oy
        cheb = abs(dx) if abs(dx) > abs(dy) else abs(dy)
        return cheb, dx * dx + dy * dy

    def min_obst_gap(nx, ny):
        if not obs:
            return 99
        best = 99
        for (x, y) in obs:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
        return best

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        m1, m2 = dist_metric(nx, ny)
        gap = min_obst_gap(nx, ny)
        # tie-break: prefer moves that keep more space from obstacles (avoid getting stuck)
        key = (m1, m2, -gap, abs(nx - (w // 2)) + abs(ny - (h // 2)), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx if (sx + dx, sy + dy) != (nx, ny) else dx, dy if (sx + dx, sy + dy) != (nx, ny) else dy)
            # If we reverted due to obstacle, ensure output matches actual position change (could be 0,0)
            if (nx, ny) == (sx, sy):
                best = (0, 0)

    return [int(best[0]), int(best[1])]