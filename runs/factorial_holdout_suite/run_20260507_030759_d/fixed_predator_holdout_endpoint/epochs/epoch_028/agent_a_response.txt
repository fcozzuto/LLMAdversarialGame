def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(map(tuple, obs_list))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Pick a target resource where we can arrive earlier than opponent (denial-aware).
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(oy - oy)
        # Strongly prefer immediately collectible; then prefer earlier arrival; then prefer being near.
        key = (od - sd, -sd, -dist2(rx, ry, w // 2, h // 2))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # If opponent is much closer to this target, try to "shadow" by moving toward the opponent's nearest resource instead.
    opp_target = None
    opp_best = None
    for prx, pry in resources:
        od = abs(prx - ox) + abs(pry - oy)
        key = (-od, dist2(prx, pry, sx, sy))
        if opp_best is None or key > opp_best:
            opp_best = key
            opp_target = (prx, pry)
    if (abs(rx - ox) + abs(ry - oy)) + 1 < (abs(rx - sx) + abs(ry - sy)):
        rx, ry = opp_target

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        landing = 1 if (nx, ny) in set(map(tuple, resources)) else 0
        # Reduce distance to target and increase distance from opponent (resource_denier).
        d_self = dist2(nx, ny, rx, ry)
        d_opp = abs(nx - ox) + abs(ny - oy)
        # Obstacle proximity (simple): prefer staying away from obstacles.
        min_obs = 0
        for (ex, ey) in obs_list:
            dd = abs(nx - ex) + abs(ny - ey)
            if dd == 0:
                min_obs = -1
                break
            if min_obs == 0 or dd < min_obs:
                min_obs = dd
        if min_obs < 0:
            continue
        score = landing * 10**9 + (1000 - d_self) + d_opp * 3 + (min_obs if min_obs else 0) * 2
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all moves blocked (rare), stay.
    return best_move