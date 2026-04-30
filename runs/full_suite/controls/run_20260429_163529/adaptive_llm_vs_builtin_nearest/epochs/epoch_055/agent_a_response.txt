def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_near_pen(nx, ny):
        best = 999
        for (hx, hy) in obstacles:
            d = dist(nx, ny, hx, hy)
            if d < best:
                best = d
                if best == 0:
                    return 10.0
        if best == 999:
            return 0.0
        # Penalize being close to obstacles (discourage running into clutter)
        return 1.5 / (1.0 + best)

    def score_from(nx, ny):
        if not resources:
            return -obs_near_pen(nx, ny)
        best_s = -10**9
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer resources we can reach earlier (or force opponent later)
            gain = (do - ds)
            # Encourage immediate grabs and slight preference for resources closer to us
            grab = 3.0 if ds == 0 else (2.0 if ds == 1 else 0.0)
            # Discourage stepping toward resources that are "too blocked" by nearby obstacles
            res_pen = obs_near_pen(rx, ry) * 0.3
            s = gain + grab - res_pen - 0.05 * ds
            if s > best_s:
                best_s = s
        return best_s - obs_near_pen(nx, ny)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles):
            # Allow, but heavily discourage invalid moves (engine keeps us in place anyway)
            val = -10**6
        else:
            val = score_from(nx, ny)
        # Deterministic tie-break: smaller (dx,dy) in listed order keeps consistency
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move