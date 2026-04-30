def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", [])
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))
    if not resources:
        target = (w // 2, h // 2)
    else:
        best_r = None
        best_val = -10**18
        for rx, ry in resources:
            myd = abs(rx - sx) + abs(ry - sy)
            opd = abs(rx - ox) + abs(ry - oy)
            val = (opd - myd) * 10 - myd
            if val > best_val:
                best_val = val
                best_r = (rx, ry)
        target = best_r
    tx, ty = target
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d_target = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Prefer reducing distance to target; also prefer staying away from opponent.
        # Strongly discourage moving where opponent is closer/equal.
        myd_now = dist((sx, sy), (tx, ty))
        oppd_now = dist((ox, oy), (tx, ty))
        oppd_next = dist((ox, oy), (tx, ty))
        opp_closer = d_target >= 0 and (abs(tx - ox) + abs(ty - oy)) <= (abs(tx - nx) + abs(ty - ny))
        score = -d_target * 100 + d_opp * 2
        score += (myd_now - d_target) * 30
        if opp_closer:
            score -= 60
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]