def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evade = ("evad" in role) or ("evad" in opp_role and "purs" not in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, x2, y2):
        return abs(x - x2) + abs(y - y2)

    def corner_bias(x, y):
        return min(x + y, x + (h - 1 - y), (w - 1 - x) + y, (w - 1 - x) + (h - 1 - y))

    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            return -10**9 if evade else -10**9
        d = dist(nx, ny, ox, oy)
        # obstacle pressure: penalize being adjacent to obstacles (can't capture them but reduces options)
        adj_obs = 0
        for ax, ay in obs:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1 and (nx, ny) != (ax, ay):
                adj_obs += 1
        center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        if evade:
            # Maximize distance; prefer corners if distance is not already dominant.
            return (d * 6.0) + (corner_bias(nx, ny) * 1.5) - (center * 0.15) - (adj_obs * 2.0)
        else:
            # Minimize distance to opponent; also avoid obstacles and edge-sticking.
            return (-d * 7.0) - (corner_bias(nx, ny) * 0.05) - (center * 0.2) - (adj_obs * 3.0)

    best = None
    bestv = None
    for dx, dy in moves:
        v = eval_move(dx, dy)
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    return best