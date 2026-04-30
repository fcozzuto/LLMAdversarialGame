def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a resource that we are closer to than the opponent (deny), otherwise the best neutral.
    best = None
    best_sc = -10**9
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer winning races to resources; also prefer advancing toward the opponent side.
        sc = (do - ds) * 10 - ds + (ry - sy) * 0.2 + (rx - sx) * 0.05
        if sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    # If no resources, move toward the opponent with slight center bias (acts like a blocker).
    if best is None:
        tx, ty = (ox + sx) / 2.0, (oy + sy) / 2.0
        tx = int(tx + 0.00001)
        ty = int(ty + 0.00001)
    else:
        tx, ty = best

    # Greedy one-step toward target, but if blocked choose best among valid moves.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Tie-break: increase opponent distance to buy time, and avoid staying if possible.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        score = -d1 * 10 + d_op * 0.3 - stay_pen
        candidates.append((score, dx, dy))
    candidates.sort(reverse=True)
    if candidates:
        _, dx, dy = candidates[0]
        return [int(dx), int(dy)]

    return [0, 0]