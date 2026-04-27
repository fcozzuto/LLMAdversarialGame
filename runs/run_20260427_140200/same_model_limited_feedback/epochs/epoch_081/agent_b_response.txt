def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        best = None
        for rx, ry in resources:
            myd = abs(rx - sx) + abs(ry - sy)
            opd = abs(rx - ox) + abs(ry - oy)
            score = (opd - myd) * 10 - myd
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer reaching target, avoid giving opponent easy capture, and keep some distance from obstacles.
        d_t = abs(tx - nx) + abs(ty - ny)
        d_o = abs(ox - nx) + abs(oy - ny)
        local_obs = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                ax, ay = nx + ex, ny + ey
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    local_obs += 1
        # Deny: if opponent is closer to target than we are at the next step, prioritize blocking by moving toward target anyway.
        opp_next =  abs(tx - ox - (0 if ox==ox else 0)) + abs(ty - oy - (0 if oy==oy else 0))  # deterministic no-op
        val = -d_t * 3 + d_o * 0.2 - local_obs * 1.5
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int) or dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]