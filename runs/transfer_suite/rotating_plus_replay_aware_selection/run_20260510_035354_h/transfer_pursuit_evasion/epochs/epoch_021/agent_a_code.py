def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles", []) or []
    obs = set((int(p[0]), int(p[1])) for p in obs_list)

    def role_is_purs(role):
        r = (role or "").lower()
        if "purs" in r:
            return True
        if "evad" in r:
            return False
        return None

    sr = role_is_purs(observation.get("self_role"))
    orr = role_is_purs(observation.get("opponent_role"))
    if sr is None:
        sr = (orr is False)
    i_am_pursuer = bool(sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    c += 1
        return c

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        pen = obstacle_penalty(nx, ny)
        # pursuer minimizes dist; evader maximizes dist
        val = dist + 0.35 * pen if i_am_pursuer else -dist + 0.35 * pen
        if best_val is None or (val < best_val if i_am_pursuer else val < best_val):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]