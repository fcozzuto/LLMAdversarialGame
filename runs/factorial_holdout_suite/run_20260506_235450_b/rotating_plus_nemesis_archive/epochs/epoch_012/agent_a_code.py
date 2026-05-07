def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            myd = None
            opd = None
            for rx, ry in resources:
                d1 = manh(nx, ny, rx, ry)
                d2 = manh(ox, oy, rx, ry)
                if myd is None or d1 < myd: myd = d1
                if opd is None or d2 < opd: opd = d2
            # Prefer moves that make us closer than opponent to some resource; slight tie-break by reducing distance to opponent.
            v = (opd - myd) * 1000 - manh(nx, ny, ox, oy)
            # Deterministic secondary: prefer closer to the chosen resource for stability
            v -= manh(nx, ny, cx, cy) * 0.01
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # No visible resources: move toward center while minimizing risk vs opponent and avoiding obstacles.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        toward = -manh(nx, ny, cx, cy)
        away = manh(nx, ny, ox, oy)
        v = toward * 10 + away
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best