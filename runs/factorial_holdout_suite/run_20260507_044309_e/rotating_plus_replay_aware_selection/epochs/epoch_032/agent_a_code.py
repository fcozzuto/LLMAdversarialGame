def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < tuple(best)):
                bestd = d
                best = [dx, dy]
        if best == [0, 0]:
            # fallback: try any in-bounds non-obstacle move
            for dx, dy in ((0,1),(1,0),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1),(0,0)):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [dx, dy]
        return best

    cx, cy = w // 2, h // 2
    best_score = -10**30
    best_target = resources[0]
    # Choose resource where we have maximal time advantage; tie-break toward closer and central.
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive => we reach earlier
        center = cheb(rx, ry, cx, cy)
        score = adv * 1000 - ds * 6 - center
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    candidates = []
    for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        # Prefer non-obstacle moves; if all blocked, allow staying.
        if (nx, ny) not in obstacles:
            candidates.append((0, cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), dx, dy))
    if not candidates:
        # all neighboring cells blocked; attempt staying if in bounds
        if (sx, sy) not in obstacles:
            return [0, 0]
        # otherwise try any in-bounds move regardless
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                return [dx, dy]
        return [0, 0]

    # Sort by (non-obstacle flag, own distance, opponent distance) then deterministic by delta
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    return [candidates[0][3], candidates[0][4]]