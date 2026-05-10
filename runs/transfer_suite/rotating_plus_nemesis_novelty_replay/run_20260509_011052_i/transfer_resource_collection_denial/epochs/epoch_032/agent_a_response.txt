def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    sprint = int(observation.get("remaining_resource_count", len(res)) or len(res)) <= 6
    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Prefer resources where we are significantly closer than opponent; otherwise prefer closer overall.
        score = (do - ds) * 1000 - ds * (3 if sprint else 1)
        if best_score is None or score > best_score or (score == best_score and (ds < best[0] or ds == best[0] and (x < best[1] or x == best[1] and y < best[2]))):
            best_score = score
            best = (ds, x, y)

    _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the diagonal step hits an obstacle, fall back deterministically to a non-blocked axis step.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in blocked:
        if dx != 0:
            nx2, ny2 = sx + dx, sy
            if (nx2, ny2) not in blocked:
                return [dx, 0]
        if dy != 0:
            nx2, ny2 = sx, sy + dy
            if (nx2, ny2) not in blocked:
                return [0, dy]
        return [0, 0]
    return [dx, dy]