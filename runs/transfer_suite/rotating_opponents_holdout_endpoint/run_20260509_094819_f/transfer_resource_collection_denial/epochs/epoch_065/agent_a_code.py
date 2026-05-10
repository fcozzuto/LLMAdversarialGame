def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def near_obstacle(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    return 1
        return 0

    best = None
    best_key = None

    for p in resources:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        x, y = int(p[0]), int(p[1])
        if not (0 <= x < w and 0 <= y < h):
            continue
        if (x, y) in obs:
            continue
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)

        # Prefer resources we can likely beat; otherwise still race but avoid obstacle-adjacent targets.
        can_win = 1 if ds < do else 0
        dist_gap = do - ds  # positive means we are closer
        key = (can_win, dist_gap, -ds, -near_obstacle(x, y), -((x + 3 * y) % 7))
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best if best is not None else (sx, sy)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Small obstacle-aware nudge: if stepping would land on obstacle, slide along the other axis.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs:
        if dx != 0 and (sx + dx, sy) not in obs:
            dx, dy = dx, 0
        elif dy != 0 and (sx, sy + dy) not in obs:
            dx, dy = 0, dy
        else:
            dx, dy = 0, 0
    return [int(dx), int(dy)]