def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (0, 0)
        best_s = -10**18
        cx, cy = w // 2, h // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            s = -king_dist(nx, ny, cx, cy) - 0.2 * king_dist(nx, ny, ox, oy)
            if s > best_s:
                best_s = s
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = -king_dist(nx, ny, ox, oy) * 0.15  # avoid moving into opponent directly
        for rx, ry in resources:
            d_me = king_dist(nx, ny, rx, ry)
            d_op = king_dist(ox, oy, rx, ry)
            margin = d_op - d_me  # positive means we are closer
            # prioritize resources we can win, also value immediate proximity
            score += (120.0 / (d_me + 1.0)) + 30.0 * margin - 0.5 * (d_me == 0)
        # slight preference for moves that keep options: fewer obstacles nearby not possible w/out extra info; use distance to nearest resource as tie-break
        if score > best_s:
            best_s = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]