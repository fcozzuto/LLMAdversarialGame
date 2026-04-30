def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def best_target_score(px, py):
        if not resources:
            return -king_dist(px, py, ox, oy) - 0.1 * king_dist(px, py, cx, cy)
        best = -10**9
        for tx, ty in resources:
            myd = king_dist(px, py, tx, ty)
            opd = king_dist(ox, oy, tx, ty)
            # Prefer winning the race to resources; slight preference for nearer center to avoid corner traps.
            win = (opd - myd)
            s = 1000 * win - 3 * myd + 0.4 * opd - 0.01 * king_dist(px, py, cx, cy)
            if s > best:
                best = s
        return best

    # Prefer moving that maximizes immediate advantage; deterministic tie-break: lexicographic on delta list order.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = best_target_score(nx, ny)
        # Add small term to prefer reducing distance to opponent when we are already behind (denies easy picks).
        val += 0.02 * (king_dist(sx, sy, ox, oy) - king_dist(nx, ny, ox, oy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]