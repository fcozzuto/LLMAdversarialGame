def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal_moves():
        out = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                out.append((dx, dy, nx, ny))
        return out

    legal = legal_moves()
    if not legal:
        return [0, 0]

    # If no resources exist, drift to center while avoiding obstacles.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, cx, cy)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) == (0, 0)):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Target with strongest positive advantage; if none, pick move that reduces my distance to some resource
    best = None  # (primary, secondary, tertiary, dx, dy)
    for dx, dy, nx, ny in legal:
        myd_best = None
        worst_delta = None
        max_delta = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            delta = od - myd
            if max_delta is None or delta > max_delta:
                max_delta = delta
            if myd_best is None or myd < myd_best:
                myd_best = myd
            # track worst (most negative) delta to avoid moving where I become significantly worse on any resource
            if worst_delta is None or delta < worst_delta:
                worst_delta = delta

        # Primary: maximize max_delta (how much I can overtake at best).
        # Secondary: if tie, maximize worst_delta (avoid broadly falling behind).
        # Tertiary: if tie, minimize myd_best (get closer overall).
        # Deterministic final tie-break: prefer (0,0) then lexicographic.
        primary = max_delta
        secondary = worst_delta
        tertiary = myd_best if myd_best is not None else 10**9
        tie_key = (0 if (dx, dy) == (0, 0) else 1, dx, dy)
        cand = (primary, secondary, -tertiary, tie_key, dx, dy)
        if best is None or cand[:4] > best[:4]:
            best = cand

    return [best[4], best[5]]