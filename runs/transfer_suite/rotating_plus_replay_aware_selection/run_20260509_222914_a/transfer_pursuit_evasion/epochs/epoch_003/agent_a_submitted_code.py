def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list if p is not None and len(p) >= 2}
    resources = observation.get("resources") or []
    res = [(r[0], r[1], r[2]) for r in resources if r is not None and len(r) >= 2]
    if not res:
        res = [(r[0], r[1], 1) for r in resources if r is not None and len(r) >= 2]
    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("run" in role)
    is_pursuer = not is_evader
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = 0
        if is_pursuer:
            score += 1000 - dist_opp * 10
        else:
            score += dist_opp * 10
        if res:
            dself = 10**9
            for rx, ry, rv in res:
                d = abs(nx - rx) + abs(ny - ry)
                if d < dself:
                    dself = d
                    closest_r = (rx, ry, rv)
            rv = closest_r[2]
            score += rv * 25 - dself * 2
        if (nx, ny) in obstacles:
            score -= 10**9
        if (best_score is None) or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]