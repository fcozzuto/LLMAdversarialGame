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
    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_pen(x, y):
        if not obstacles:
            return 0.0
        best = 999
        for (hx, hy) in obstacles:
            d = dist(x, y, hx, hy)
            if d < best:
                best = d
                if best == 0:
                    return 5.0
        if best == 999:
            return 0.0
        return 0.9 / (1.0 + best)

    # Pick target resource: prefer ones we can reach earlier than opponent (margin)
    best_r = None
    best_gain = -10**9
    for (rx, ry) in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        gain = (do - ds)  # positive means we are closer
        # slight tie-break: avoid resources deep in clutter
        gain -= 0.3 * obs_pen(rx, ry)
        # slight preference for not-too-far
        gain -= 0.02 * ds
        if gain > best_gain:
            best_gain = gain
            best_r = (rx, ry)

    rx, ry = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            v = -1e9
        else:
            d_new = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, nx, ny)  # discourage moving into opponent range slightly
            v = -d_new + 0.12 * d_op - 1.2 * obs_pen(nx, ny)
            # If we step onto an obstacle-adjacent cell, avoid; already covered by obs_pen.
        if v > best_v:
            best_v = v
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]