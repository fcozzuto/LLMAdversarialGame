def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs if isinstance(p, (list, tuple)) and len(p) >= 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            v = -d
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    def mindist(x, y):
        m = None
        for rx, ry in resources:
            d = abs(x - rx) + abs(y - ry)
            if m is None or d < m:
                m = d
        return m if m is not None else 0

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd = mindist(nx, ny)
        opd = mindist(ox, oy)
        advantage = opd - myd
        danger = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if (ax, ay) in obstacles:
                    danger += 1
        score = advantage * 100 - myd * 2 - danger
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]