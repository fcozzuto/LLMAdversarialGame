def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def best_resource_dist(x, y):
        if not resources:
            return 0
        m = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if m is None or d < m:
                m = d
        return m if m is not None else 0

    curr_d = best_resource_dist(sx, sy)
    best_move = (0, 0)
    best_primary = None
    best_secondary = None

    # Updated strategy: prioritize reducing distance to nearest resource, but keep away from opponent
    # (meaningful change vs "just chase" policies).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = best_resource_dist(nx, ny)
        od = cheb(nx, ny, ox, oy)
        primary = -nd  # maximize (equiv minimize nd)
        secondary = od + (curr_d - nd) * 0.25  # prefer improving resource distance and staying farther from opponent
        if best_primary is None or primary > best_primary or (primary == best_primary and secondary > best_secondary):
            best_primary = primary
            best_secondary = secondary
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]