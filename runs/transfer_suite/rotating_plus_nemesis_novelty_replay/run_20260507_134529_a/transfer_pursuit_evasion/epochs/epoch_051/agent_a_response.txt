def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    far_corner = max(corners, key=lambda t: man(t[0], t[1], sx, sy))
    # If we are evader, this matches how pursuer likely "thinks"; if we are pursuer, it blocks that tendency.

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d_opp = man(nx, ny, ox, oy)
        d_corner = man(nx, ny, far_corner[0], far_corner[1])
        m = mobility(nx, ny)

        if self_is_evader:
            # Run toward the farthest corner while avoiding traps via mobility.
            # Also slightly prefer moving away from the current opponent position even if corner progress stalls.
            val = 3.0 * d_opp + 0.9 * (-d_corner) + 0.25 * m
        else:
            # Pursue while steering to block the evader's likely corner plan.
            val = -3.2 * d_opp - 0.7 * d_corner + 0.25 * m

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]
    return [int(best[0]), int(best[1])]