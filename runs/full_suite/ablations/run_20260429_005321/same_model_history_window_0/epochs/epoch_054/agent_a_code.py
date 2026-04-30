def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obstacles_raw = observation.get("obstacles", None)
    obstacles = set()
    if obstacles_raw:
        for p in obstacles_raw:
            if p and len(p) >= 2:
                obstacles.add((p[0], p[1]))

    resources = observation.get("resources", None)
    if not resources:
        resources = []

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    viable = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            viable.append((dx, dy, nx, ny))
    if not viable:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in viable:
            best_gap = None
            best_ds = None
            for rx, ry in resources:
                ds = dist(rx, ry, nx, ny)
                do = dist(rx, ry, ox, oy)
                gap = do - ds  # larger is better (we arrive sooner)
                if best_gap is None or gap > best_gap or (gap == best_gap and ds < best_ds):
                    best_gap = gap
                    best_ds = ds
            cand = (best_gap, -(best_ds if best_ds is not None else 10**9), dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[2], best[3]]

    # No resources visible: move away from opponent if possible, else stay.
    best = None
    for dx, dy, nx, ny in viable:
        gap = dist(nx, ny, ox, oy)
        cand = (gap, -abs(dx) - abs(dy), dx, dy)
        if best is None or cand > best:
            best = cand
    return [best[2], best[3]]