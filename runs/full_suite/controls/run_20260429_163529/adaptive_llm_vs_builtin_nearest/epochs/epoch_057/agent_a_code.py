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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_pen(x, y):
        if not obstacles:
            return 0.0
        best = 99
        for (hx, hy) in obstacles:
            d = man(x, y, hx, hy)
            if d < best:
                best = d
        if best <= 0:
            return 10.0
        return 0.7 / (1.0 + best)

    # Target: maximize (opponent advantage over us) = d_op - d_self
    best_t = None
    best_val = -10**9
    for (rx, ry) in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can secure earlier; lightly penalize being near obstacles.
        val = (do - ds) - 0.08 * ds - 0.35 * obs_pen(rx, ry)
        if val > best_val:
            best_val = val
            best_t = (rx, ry)
        elif val == best_val and best_t is not None:
            # deterministic tie-break: smaller ds, then lexicographic
            ds_b = man(sx, sy, best_t[0], best_t[1])
            if ds < ds_b or (ds == ds_b and (rx, ry) < best_t):
                best_t = (rx, ry)

    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Greedy step toward target, with obstacle avoidance and small bias toward cutting off opponent (through target race).
        d_self = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # If we move closer than opponent relative to target, increase score.
        # (Opponent won't move now; this biases toward targets where we can establish lead.)
        rel = (d_opp - d_self)
        s = rel - 0.06 * d_self - 0.6 * obs_pen(nx, ny)
        if s > best_s:
            best_s = s
            best_m = (dx, dy)
        elif s == best_s:
            if (dx, dy) < best_m:
                best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]