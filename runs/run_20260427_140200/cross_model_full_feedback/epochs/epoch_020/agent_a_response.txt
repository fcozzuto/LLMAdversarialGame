def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cands = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cands.append((dx, dy, nx, ny))
    if not cands:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    center = (cx, cy)
    best = None
    best_score = -10**18

    if resources:
        for dx, dy, nx, ny in cands:
            myd_op = dist((nx, ny), (ox, oy))
            # Prefer moves that secure contested resources:
            # score considers advantage over opponent for a resource we can reach now.
            score = -0.05 * myd_op  # don't drift into opponent
            local_best = -10**18
            for rx, ry in resources:
                d_self = abs(nx - rx) + abs(ny - ry)
                d_opp = abs(ox - rx) + abs(oy - ry)
                # Bigger is better: (opponent slower) + proximity pressure for contested
                adv = (d_opp - d_self)
                cont = 8 - min(d_self, d_opp)  # focus on nearer fights
                val = adv * 10 + cont * (1 if d_self <= d_opp else -1)
                # Tiny tie-break towards center to avoid cycles
                val -= 0.01 * (abs(nx - center[0]) + abs(ny - center[1]))
                if val > local_best:
                    local_best = val
            score += local_best
            # Deterministic tie-break: prefer smaller dx, then smaller dy
            if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
                best_score = score
                best = (dx, dy)
    else:
        # No visible resources: move toward center while staying farther from opponent
        for dx, dy, nx, ny in cands:
            myd_op = dist((nx, ny), (ox, oy))
            to_center = abs(nx - center[0]) + abs(ny - center[1])
            score = myd_op * 10 - to_center
            if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]