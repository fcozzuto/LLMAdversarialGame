def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # drift toward opponent a bit to reduce their escape value
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose target resource where we are relatively closer than opponent.
    best_t = resources[0]
    best_tv = -10**18
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; penalize long routes.
        tv = (od - md) * 10 - md
        if tv > best_tv:
            best_tv, best_t = tv, (rx, ry)

    tx, ty = best_t

    # One-step look: maximize improvement toward target, and avoid being too close to opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d1 = cheb(sx, sy, tx, ty)
        d2 = cheb(nx, ny, tx, ty)
        toward = d1 - d2  # positive if closer
        # If opponent is also near, slightly prefer staying/advancing to avoid giving them immediate capture.
        oppd = cheb(nx, ny, ox, oy)
        opp_term = oppd * 0.2
        val = toward * 10 - d2 * 0.5 + opp_term
        if val > best_val:
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]