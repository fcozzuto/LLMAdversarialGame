def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if inb(bx, by):
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    # Pick a target we can beat (in time), tie-break by closer to us and not blocked
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        cand = (opd - myd, -myd, rx, ry)
        if best is None or cand > best:
            best = cand
    tx, ty = best[2], best[3]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def move_score(nx, ny):
        # Hard avoid obstacles
        if (nx, ny) in obstacles:
            return -10**9
        # Prefer progress toward target and denying opponent
        my_now = cheb(nx, ny, tx, ty)
        opp_now = cheb(ox, oy, tx, ty)
        my_cur = cheb(sx, sy, tx, ty)
        # If my move would make it worse than staying still, discourage slightly
        stay_my = my_cur
        progress = (stay_my - my_now)
        deny = (opp_now - my_now)
        # Mild penalty for moving adjacent to obstacle to reduce collisions
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_pen += 1
        return progress * 3 + deny * 2 - adj_pen

    best_move = (0, 0)
    best_sc = -10**18
    # Deterministic tie-break: prefer lower dx/dy lexicographically
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = move_score(nx, ny)
        key = (sc, -abs(dx), -abs(dy), - (dx * 10 + dy))
        if key[0] > best_sc:
            best_sc = key[0]
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]