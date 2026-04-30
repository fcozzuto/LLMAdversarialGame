def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_cnt(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    # Choose resource we are most likely to secure: maximize (opp_dist - self_dist).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        if sd == 0:
            key = (10**9, 0, 0, rx, ry)
        else:
            # Bias toward closer, also avoid areas adjacent to obstacles.
            key = (
                od - sd,              # win margin
                -sd,                  # closer for us
                -abs(rx - ox) - abs(ry - oy),  # reduce opponent spread
                -obs_cnt(rx, ry),     # safer resource location
                -rx, -ry,
            )
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move that reduces our distance to target while keeping us away from obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = manh(nx, ny, tx, ty)
        d_opp = manh(ox, oy, tx, ty)
        # Prefer improving our win margin (if opponent distance changes via target pick only, it's constant here),
        # so primarily minimize our distance and penalize obstacle-adjacent squares.
        val = (
            d_self,                 # minimize
            obs_cnt(nx, ny),        # avoid obstacles
            -d_opp,                 # slight preference to keep opponent far (consistent tie-break)
            dx, dy
        )
        if best_val is None or val < best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]