def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            res.append((x, y))

    if not res or (sx, sy) in obs:
        return [0, 0]
    if (sx, sy) in obs:
        return [0, 0]
    if (sx, sy) in res:
        return [0, 0]

    def cheb(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obs_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if nx >= 0 and nx < w and ny >= 0 and ny < h and (nx, ny) in obs:
                    pen += 2
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Choose a target that we can arrive at earlier; otherwise deny by maximizing opponent delay.
        best_val = None
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # We prefer immediate collection, then targets where we have a distance advantage.
            immediate = 1000 if sd == 0 else 0
            advantage = (od - sd)  # positive is good
            # Small tie-break: prefer closer when values are similar, and avoid obstacles.
            v = immediate + advantage * 20 - sd - adj_obs_pen(nx, ny) * 1
            if best_val is None or v > best_val:
                best_val = v
        if best_val is None:
            continue
        # Deterministic secondary: closer to opponent is slightly better only if equal; avoids oscillation.
        tieb = cheb(nx, ny, ox, oy)
        cand = (best_val, -tieb, -dx, -dy)
        if best is None or cand > best:
            best = cand
            best_move = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]