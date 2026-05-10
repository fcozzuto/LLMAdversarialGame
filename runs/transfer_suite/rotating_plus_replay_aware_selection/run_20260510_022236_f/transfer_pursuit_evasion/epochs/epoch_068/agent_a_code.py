def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_obs_d(x, y):
        if not obs:
            return 10**6
        d = 10**6
        for ax, ay in obs:
            t = abs(x - ax) + abs(y - ay)
            if t < d:
                d = t
        return d

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        target = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        # If multiple corners tie, bias toward approaching opponent instead
        if len(corners) > 0:
            target = max(corners, key=lambda c: -abs(c[0] - ox) - abs(c[1] - oy))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in obs:
            nx, ny = sx, sy

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_tgt = abs(nx - target[0]) + abs(ny - target[1])
        nd_obs = nearest_obs_d(nx, ny)

        if is_evader:
            val = d_opp * 10 - d_tgt - (3.0 / (1 + nd_obs))
        else:
            val = (-d_opp) * 10 - d_tgt - (3.0 / (1 + nd_obs))

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]