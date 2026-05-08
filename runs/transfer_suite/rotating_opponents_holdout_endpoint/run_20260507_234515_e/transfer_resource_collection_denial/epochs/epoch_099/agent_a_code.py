def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    rem = int(observation.get("remaining_resource_count", len(resources)))
    turns_left = int(observation.get("turns_remaining", 0))

    target = None
    best = None
    aggressive = (rem <= 4) or (turns_left <= 10)
    for r in resources:
        x, y = int(r[0]), int(r[1])
        if (x, y) in obstacles:
            continue
        ds = dist_cheb(sx, sy, x, y)
        do = dist_cheb(ox, oy, x, y)
        if (not aggressive) and do < ds:
            continue
        corner_bias = (x == 0 or x == w - 1) + (y == 0 or y == h - 1)
        # If aggressive, allow slightly contested but prefer closer
        value = ds - (0.45 if aggressive else 0.0) * (ds == 0) + 0.35 * (8 - do) - 0.12 * corner_bias
        if best is None or value < best:
            best = value
            target = (x, y)

    if target is None:
        # Default: go toward opponent-weak side (toward nearest corner to deny)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: dist_cheb(sx, sy, c[0], c[1]))
    else:
        tx, ty = target

    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to = dist_cheb(nx, ny, tx, ty)
            d_opp = dist_cheb(nx, ny, ox, oy)
            # Prefer moves that reduce distance to target; also avoid letting opponent get closer while we stand still
            val = d_to - 0.08 * d_opp + (0.2 if (dx == 0 and dy == 0) else 0.0)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move