def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose best resource by "we arrive earlier than opponent" (chebyshev distance)
    best_t = None
    best_rank = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        if best_rank is None or (od - sd, -sd) > best_rank:
            best_rank = (od - sd, -sd)
            best_t = (tx, ty)

    tx, ty = best_t
    # Evaluate one-step moves toward the chosen target, but avoid obstacles
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        val = (no - ns, -ns)  # maximize arrival advantage, then closeness
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    # Fallback if all invalid (shouldn't happen)
    if best_val is None:
        return [0, 0]
    return best_move