def choose_move(observation):
    def gi(v, d=0):
        try:
            return int(v)
        except:
            return d

    w = gi(observation.get("grid_width", 8), 8) or 8
    h = gi(observation.get("grid_height", 8), 8) or 8

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = gi(sp[0], 0), gi(sp[1], 0)
    ox, oy = gi(op[0], 0), gi(op[1], 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = gi(p[0], 0), gi(p[1], 0)
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        x, y = gi(r[0], 0), gi(r[1], 0)
        if inside(x, y):
            targets.append((x, y))
    if not targets:
        tx, ty = ox, oy
    else:
        best = None
        for (x, y) in targets:
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            lead = od - sd
            score = lead * 1000 - sd
            if best is None or score > best[0] or (score == best[0] and sd < best[1]):
                best = (score, sd, x, y)
        tx, ty = best[2], best[3]

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        dself = cheb(nx, ny, tx, ty)
        dread = 0
        if targets:
            # slight anti-opponent: prefer decreasing (oppdist - selfdist) at next step
            for (x, y) in targets:
                if cheb(x, y, tx, ty) == 0:
                    dread = cheb(ox, oy, x, y) - cheb(nx, ny, x, y)
                    break
        # deterministic tie-breaker by move order
        score = -dself * 1000 + dread
        if best_move is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move