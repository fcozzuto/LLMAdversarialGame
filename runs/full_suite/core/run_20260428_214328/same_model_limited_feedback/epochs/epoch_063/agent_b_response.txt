def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs_set = set((p[0], p[1]) for p in obstacles)
    res_set = set((p[0], p[1]) for p in resources)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_move = [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        if (nx, ny) in res_set:
            res_bonus = 100.0
        else:
            res_bonus = 0.0

        nearest = 10**9
        for rx, ry in resources:
            d = max(0, manh(nx, ny, rx, ry) - 0)  # deterministic
            if d < nearest:
                nearest = d

        dist_to_opp = manh(nx, ny, ox, oy)
        # Prefer holding space slightly away from opponent unless grabbing resource
        opp_pen = 0.15 * (8 - min(8, dist_to_opp))
        # Prefer moving closer to resources; also discourage staying if not on resource
        stay_pen = 0.2 if (dx == 0 and dy == 0) else 0.0

        score = res_bonus - nearest - opp_pen - stay_pen

        if best is None or score > best or (score == best and (dx, dy) < tuple(best_move)):
            best = score
            best_move = [dx, dy]

    return best_move