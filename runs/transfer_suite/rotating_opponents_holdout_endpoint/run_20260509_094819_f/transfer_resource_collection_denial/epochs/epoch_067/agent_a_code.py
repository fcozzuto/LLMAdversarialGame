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

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obst(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    return 1
        return 0

    best_t = None
    best_cell = None
    for p in resources:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        x, y = int(p[0]), int(p[1])
        if not inb(x, y) or (x, y) in obs:
            continue
        self_d = cheb(sx, sy, x, y)
        opp_d = cheb(ox, oy, x, y)
        t = self_d - 1.2 * opp_d
        t += 0.35 * adj_obst(x, y)
        if best_t is None or t < best_t or (t == best_t and self_d < best_cell[0]):
            best_t = t
            best_cell = (self_d, x, y)

    if best_cell is None:
        return [0, 0]

    _, tx, ty = best_cell

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obs:
        return [dx, dy]

    # fallback: greedily try among 8 dirs + stay, preferring reducing cheb and avoiding obstacles
    best = None
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            cx, cy = sx + mx, sy + my
            if not inb(cx, cy) or (cx, cy) in obs:
                continue
            d = cheb(cx, cy, tx, ty)
            score = d
            score += 2.0 * adj_obst(cx, cy)
            # also slightly prefer being ahead of opponent toward same target
            score -= 0.15 * (cheb(ox, oy, tx, ty) - d)
            if best is None or score < best[0]:
                best = (score, mx, my)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]