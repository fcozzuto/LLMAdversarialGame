def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    opp_front = set()
    for x, y in opp_t:
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_t:
                opp_front.add((nx, ny))

    candidates = []
    frontier_targets = [(x, y) for (x, y) in opp_front if (x, y) in unclaimed or (x, y) in opp_t]
    if frontier_targets:
        candidates = frontier_targets
    else:
        candidates = [c for c in unclaimed if c not in obstacles] or [(ox, oy)]

    my_count = int(observation.get("self_territory_count") or len(self_t))
    op_count = int(observation.get("opponent_territory_count") or len(opp_t))
    need_attack = my_count <= op_count

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score_cell(x, y):
        dx1 = x - sx
        dy1 = y - sy
        d = dx1 * dx1 + dy1 * dy1
        to_op = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        on_front = 1 if (x, y) in opp_front else 0
        un = 1 if (x, y) in unclaimed else 0
        center = (x - cx) * (x - cx) + (y - cy) * (y - cy)
        if need_attack:
            return 5 * d - 30 * on_front - 8 * un + 0.2 * to_op + 0.01 * center
        return 5 * d + 0.2 * to_op - 4 * on_front - 6 * un + 0.01 * center

    best = None
    for x, y in candidates:
        if not inb(x, y) or (x, y) in obstacles:
            continue
        k = score_cell(int(x), int(y))
        if best is None or k < best[0]:
            best = (k, int(x), int(y))

    tx, ty = (best[1], best[2]) if best else (ox, oy)

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]

    # Fallback: choose best reachable neighbor by same scoring toward (tx, ty)
    best2 = None
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        k = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if best2 is None or k < best2[0]:
            best2 = (k, ddx, ddy)
    return [best2[1], best2[2]]