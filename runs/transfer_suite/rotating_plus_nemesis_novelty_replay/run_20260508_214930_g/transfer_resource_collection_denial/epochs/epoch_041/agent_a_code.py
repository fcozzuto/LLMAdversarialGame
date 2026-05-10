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
            obs.add((int(p[0]), int(p[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_margin(px, py):
        bm = -10**9
        best_d = 10**9
        for rx, ry in res:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            m = od - sd
            if m > bm or (m == bm and sd < best_d):
                bm = m
                best_d = sd
        return bm, best_d

    best_move = (0, 0)
    best_primary = -10**9
    best_secondary = 10**9
    best_tertiary = 10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        primary, d_to_resource = best_margin(nx, ny)
        # Stronger tie-break: avoid positions that give opponent a likely win immediately
        opp_best_margin_now, _ = best_margin(ox, oy)  # constant-ish but deterministic
        # Lower tertiary is better: keep progress toward our best target from current position
        _, d_now = best_margin(sx, sy)
        tertiary = d_now
        if primary > best_primary:
            best_primary = primary
            best_secondary = d_to_resource
            best_tertiary = tertiary
            best_move = (dx, dy)
        elif primary == best_primary:
            if d_to_resource < best_secondary:
                best_secondary = d_to_resource
                best_tertiary = tertiary
                best_move = (dx, dy)
            elif d_to_resource == best_secondary:
                if tertiary < best_tertiary:
                    best_tertiary = tertiary
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]