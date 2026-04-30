def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def nearest_dist(x, y):
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    opp_best_now = nearest_dist(ox, oy)

    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in cand:
        myd = 10**9
        op_d = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            if d1 < myd: myd = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < op_d: op_d = d2

        # If opponent is close to some resource, prioritize moving to improve our min distance.
        # Also prefer moves that don't let opponent get dramatically closer to any remaining resource.
        opp_best_after = opp_best_now  # opponent position doesn't change on our turn
        # Micro-avoid: slightly penalize adjacency to obstacles to reduce bumping.
        adj_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if (ax, ay) in obstacles:
                    adj_obs += 1

        score = (-1000 * myd) + (-10 * adj_obs) + (-1 * op_d) + (-2 * (opp_best_after))
        # Deterministic tie-break: prefer staying on grid center-ish, then lexicographic dx,dy
        score += -0.001 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        if score > best_score or (score == best_score and (dx, dy, nx, ny) < (best_move[0], best_move[1], best_move[2], best_move[3]) if best_move else False):
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]