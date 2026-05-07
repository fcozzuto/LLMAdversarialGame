def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mhd(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not inb(sx, sy):
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            sd = mhd(sx, sy, rx, ry)
            od = mhd(ox, oy, rx, ry)
            lead = od - sd  # positive means we arrive sooner
            # small tie-break: avoid resources aligned with opponent to reduce sweep risk
            align_pen = -1 if (rx == ox or ry == oy) else 0
            score = lead * 10 + align_pen - sd
            if best is None or score > best[0]:
                best = (score, rx, ry)
        _, tx, ty = best
    else:
        tx = 0 if ox > sx else w - 1
        ty = 0 if oy > sy else h - 1

    # Greedy step toward target with obstacle avoidance
    curd = mhd(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = mhd(nx, ny, tx, ty)
        # prefer progress; slight penalty for moving to positions adjacent to opponent
        adj = max(abs(nx - ox), abs(ny - oy))
        val = (curd - nd) * 100 - nd + (5 if adj > 1 else -5)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]