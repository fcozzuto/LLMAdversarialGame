def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    def clamp_step(x, y):
        dx = 0 if x == sx else (1 if x > sx else -1)
        dy = 0 if y == sy else (1 if y > sy else -1)
        nx, ny = sx + dx, sy + dy
        return (dx, dy) if valid(nx, ny) else (0, 0)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        return list(clamp_step(tx, ty))

    res = [tuple(r) for r in resources]

    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Primary: maximize best "grab margin" over all visible resources:
        # margin = (opponent_dist - self_dist). Higher means more likely we take first.
        best_margin = -10**9
        for rx, ry in res:
            m = dist(ox, oy, rx, ry) - dist(nx, ny, rx, ry)
            if m > best_margin:
                best_margin = m

        # Secondary: minimize our distance to the closest resource (to convert when margins are tied).
        dmin = 10**9
        for rx, ry in res:
            d = dist(nx, ny, rx, ry)
            if d < dmin:
                dmin = d

        # Tertiary: prefer moves that don't let opponent get strictly better margin next.
        # (compute ourselves vs opponent at same target giving worst disadvantage)
        worst_disadv = -10**9
        for rx, ry in res:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            worst_disadv = max(worst_disadv, self_d - opp_d)

        val = (best_margin, -dmin, -worst_disadv)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]