def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # We want to beat opponent on target resource; if close, prioritize our progress.
    # Also bias to avoid mirroring opponent sweep by lightly preferring resources on our advancing axis.
    my_corner_bias = 1 if (sx + sy) % 2 == 0 else -1

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        local_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            # Positive means we are closer than opponent (good). Large weight to secure priority.
            lead = od - sd
            val = lead * 2000 - sd

            # Tie-break: prefer resources that are farther along our corner "direction"
            # (deterministic proxy for breaking sweep-row races).
            prog = (rx + ry) * my_corner_bias
            val += prog

            # Micro tie-break: parity stabilization
            val += ((sd + rx + ry) % 2)

            if val > local_best:
                local_best = val

        if local_best > best_val:
            best_val = local_best
            best_move = [nx - sx, ny - sy]

    return best_move