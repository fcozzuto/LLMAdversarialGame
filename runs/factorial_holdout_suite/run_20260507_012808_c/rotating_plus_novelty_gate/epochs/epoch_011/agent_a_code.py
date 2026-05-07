def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    if not resources:
        return [0, 0]

    # Pick a target: prioritize resources where opponent is relatively closer (deny them),
    # but still ensure we are not excessively far behind for robustness.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds == 0:
            return [0, 0]
        # Key: lower is better. Strongly deny resources opponent is closer to.
        # Add small tie-break by absolute closeness to us.
        key = (do - ds, ds + 0.1 * (rx + ry))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Intercept tweak for row-sweep: if opponent is in same row, try to align our x
    # toward the nearest resource on that row.
    if oy == sy:
        same_row = [r for r in resources if r[1] == sy]
        if same_row:
            # Choose nearest on that row to opponent (most likely to be contested soon).
            rx, ry = ox, sy
            tr = min(same_row, key=lambda p: cheb(ox, oy, p[0], p[1]))
            tx, ty = tr

    # Choose move that reduces distance to target; avoid obstacles.
    bestm = [0, 0]
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        if cheb(nx, ny, tx, ty) == 0 and (tx, ty) in resources:
            return [dx, dy]
        v = cheb(nx, ny, tx, ty)
        # small repulsion from obstacles and staying too close to opponent if target already denied
        if cheb(nx, ny, ox, oy) <= 1:
            v += 0.15
        if bestv is None or v < bestv:
            bestv = v
            bestm = [dx, dy]

    return bestm