def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles_raw = observation.get("obstacles", [])
    obstacles = set(tuple(p) for p in obstacles_raw)
    resources = observation.get("resources", [])
    # resources may be list of positions or dict-like; normalize to positions
    rpos = []
    if isinstance(resources, dict):
        for p in resources.keys():
            if isinstance(p, (list, tuple)) and len(p) == 2:
                rpos.append((p[0], p[1]))
    else:
        for p in resources:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                rpos.append((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    opp_d = man((sx, sy), (ox, oy))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    center = (cx, cy)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = man((nx, ny), (ox, oy))
        # If adjacent to opponent, strongly prefer moving away
        if opp_d <= 1:
            score = nd * 1000
        else:
            if rpos:
                nearest_r = 10**9
                for rp in rpos:
                    d = abs(nx - rp[0]) + abs(ny - rp[1])
                    if d < nearest_r:
                        nearest_r = d
                score = -nearest_r * 10
            else:
                score = -(abs(nx - center[0]) + abs(ny - center[1])) * 2
            # Mild opponent avoidance
            score += nd * 2
        # Deterministic tie-break: prefer staying if equal, else lower dx then lower dy
        if best is None or score > best_score or (score == best_score and (dx, dy) > best[0]):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]