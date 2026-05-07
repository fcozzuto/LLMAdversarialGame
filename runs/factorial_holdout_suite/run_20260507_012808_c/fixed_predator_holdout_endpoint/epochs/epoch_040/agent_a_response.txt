def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_towards(cx, cy, tx, ty):
        dx = 0
        if tx > cx: dx = 1
        elif tx < cx: dx = -1
        dy = 0
        if ty > cy: dy = 1
        elif ty < cy: dy = -1
        return dx, dy

    best = None
    best_key = None
    for (rx, ry) in resources:
        d_self = cheb((sx, sy), (rx, ry))
        d_opp = cheb((ox, oy), (rx, ry))
        lead = d_opp - d_self  # positive means we reach earlier (with diagonal moves)
        dist_bias = d_self
        # Prefer earlier lead; break ties by shorter self distance; then deterministic by coordinates
        key = (lead, -dist_bias, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx, dy = step_towards(sx, sy, tx, ty)

    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
        # Deterministically try alternative axis-aligned/diagonal moves that reduce distance
        candidates = [(-dx, dy), (dx, -dy), (-dx, -dy), (dx, 0), (0, dy), (0, 0)]
        chosen = (0, 0)
        chosen_d = None
        for cx, cy in candidates:
            nx2, ny2 = sx + cx, sy + cy
            if 0 <= nx2 < w and 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                dd = cheb((nx2, ny2), (tx, ty))
                if chosen_d is None or dd < chosen_d or (dd == chosen_d and (cx, cy) < chosen):
                    chosen_d = dd
                    chosen = (cx, cy)
        dx, dy = chosen

    return [int(dx), int(dy)]