def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    resources = observation.get("resources") or []
    rpos = []
    for p in resources:
        try:
            rpos.append((p[0], p[1]))
        except Exception:
            pass

    def blocked(x, y):
        return x < 0 or x >= w or y < 0 or y >= h or (x, y) in obstacles

    def manh(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestv = -10**18
    cx, cy = (w - 1) // 2, (h - 1) // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        toward = 0
        if rpos:
            md = 10**9
            for rx, ry in rpos:
                d = manh(nx, ny, rx, ry)
                if d < md:
                    md = d
            toward = -md
        else:
            toward = -manh(nx, ny, cx, cy)
        away_op = -manh(nx, ny, ox, oy) * 0.2
        center = -manh(nx, ny, cx, cy) * 0.05
        v = toward + away_op + center
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]