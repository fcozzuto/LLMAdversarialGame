def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obstacle_set = set((p[0], p[1]) for p in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        tx, ty = clamp((x + ox)//2, 0, w-1), clamp((y + oy)//2, 0, h-1)
    else:
        best = None
        best_val = None
        for rx, ry in resources:
            myd = abs(rx - x) + abs(ry - y)
            opd = abs(rx - ox) + abs(ry - oy)
            val = (myd - opd, myd, rx, ry)
            if best_val is None or val < best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If opponent is clearly closer to the chosen target, retarget to something they are worse at
    if resources:
        myd0 = dist(x, y, tx, ty)
        opd0 = dist(ox, oy, tx, ty)
        if opd0 + 1 <= myd0:
            best = None
            best_val = None
            for rx, ry in resources:
                myd = dist(x, y, rx, ry)
                opd = dist(ox, oy, rx, ry)
                # maximize our advantage: smaller (opd - myd), i.e. opponent far / we close
                val = ((opd - myd), myd, rx, ry)
                if best_val is None or val < best_val:
                    best_val = val
                    best = (rx, ry)
            tx, ty = best

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue

        d_to_target = dist(nx, ny, tx, ty)
        d_to_opp = dist(nx, ny, ox, oy)

        # Avoid obstacles locally and prefer reducing target distance; also modestly reduce opponent access.
        near_obs = 0
        for ox2, oy2 in obstacles:
            if abs(ox2 - nx) <= 1 and abs(oy2 - ny) <= 1:
                near_obs += 1
        if d_to_target == 0:
            score = 1e9 - near_obs * 100
        else:
            score = (-d_to_target * 10) + (-near_obs * 25) + (d_to_opp * 1)

        # Deterministic tie-breaker by dirs ordering (already fixed)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]