def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx + dy

    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int) and inb(rx, ry):
                rs.append((rx, ry))
    if not rs:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    # Score moves by how much closer we become than the opponent to the "best" resource,
    # with a small preference for reducing our distance to avoid stalling.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_pos = (nx, ny)

        # Evaluate best target for us from this candidate move
        best_t = None
        best_t_val = -10**18
        for t in rs:
            myd = md(my_pos, t)
            opd = md((ox, oy), t)
            # Primary: maximize advantage (opd - myd). Secondary: pick smaller myd.
            t_val = (opd - myd) * 100 - myd
            if t_val > best_t_val:
                best_t_val = t_val
                best_t = t

        # Encourage taking a resource sooner (or deny opponent by positive advantage)
        # plus ensure progress to avoid local traps.
        if best_t is None:
            move_val = -10**18
        else:
            myd = md((nx, ny), best_t)
            opd = md((ox, oy), best_t)
            progress = (md((sx, sy), best_t) - myd)
            move_val = (opd - myd) * 100 + progress * 5 - myd * 0.5

        # Deterministic tie-break: lexicographic on delta
        if move_val > best_val or (move_val == best_val and (dx, dy) < best):
            best_val = move_val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]