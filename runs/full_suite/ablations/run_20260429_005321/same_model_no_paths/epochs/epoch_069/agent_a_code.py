def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    if not (0 <= sx < w and 0 <= sy < h) or not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Strategic shift: pick resource where we are (strictly) closer than opponent; otherwise contest the closest.
    best_t = None
    best = None
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher is better: prefer negative gap (we closer), then lower our distance, then stable tie-break by coords.
        gap = ds - do
        key = (-(gap), -ds, -((rx + 1) * 100 + (ry + 1)))
        if best is None or key > best:
            best = key
            best_t = (rx, ry)

    tx, ty = best_t

    # One-step greedy with obstacle-avoidance and anti-oscillation via bias toward continuing direction.
    mx = 0 if tx == sx else (1 if tx > sx else -1)
    my = 0 if ty == sy else (1 if ty > sy else -1)
    primary = (mx, my)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Score: prefer closer to target; prefer primary direction; avoid null move if possible.
            dist = cheb(nx, ny, tx, ty)
            dir_bonus = 0
            if (dx, dy) == primary:
                dir_bonus = 5
            if dx == 0 and dy == 0:
                dir_bonus -= 2
            # Small penalty for moving away from opponent when contesting (encourage capture race).
            opp_dist_change = cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty)
            candidates.append((dist, -(dir_bonus), abs(dx) + abs(dy), opp_dist_change, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][4]), int(candidates[0][5])]