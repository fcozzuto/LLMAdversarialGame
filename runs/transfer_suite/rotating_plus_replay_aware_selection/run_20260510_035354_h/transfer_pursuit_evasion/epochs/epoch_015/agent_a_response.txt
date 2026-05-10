def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def wall_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    obs_list = list(observation.get("obstacles", []))
    has_obs = len(obs_list) > 0

    def nearest_obs_d2(x, y):
        if not has_obs:
            return 999999
        best = 999999
        for p in obs_list:
            px, py = p[0], p[1]
            d = dist2(x, y, px, py)
            if d < best:
                best = d
        return best

    bestv = None
    bestm = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        nd2 = nearest_obs_d2(nx, ny)
        wd = wall_dist(nx, ny)

        if i_am_pursuer:
            # Chase while gently avoiding getting too cornered; also value moving near edges to constrain.
            v = -d2 + 0.08 * wd - 0.02 * (1.0 / (1.0 + nd2)) * 100.0 + 0.001 * (nx + 2 * ny)
        else:
            # Evade: maximize distance, avoid walls, and steer away from obstacles.
            v = d2 - 0.55 * (1 if wd == 0 else wd) - 0.02 * (1.0 / (1.0 + nd2)) * 100.0 + 0.001 * (nx + 2 * ny)

        if bestv is None or v > bestv:
            bestv = v
            bestm = [dx, dy]

    return bestm