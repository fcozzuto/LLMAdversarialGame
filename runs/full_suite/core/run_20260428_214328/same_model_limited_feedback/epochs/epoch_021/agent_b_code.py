def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Fallback: move slightly toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            cand = (d, dx, dy)
            if cand < best:
                best = cand
        return [best[1], best[2]]

    # Choose resource to race for: prioritize being closer than opponent, then minimize our distance
    best_res = None
    best_key = (10**18, 10**9, 10**9)  # (key1, self_dist, x, y)
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # If we are closer/equal, strongly preferred; otherwise deprioritize
        key1 = (0 if sd <= od else 1000) + (sd - od)
        key = (key1, sd, rx, ry)
        if key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    # Greedy step toward chosen resource; if blocked, choose best alternative that reduces our distance
    target_dx = 0 if rx == sx else (1 if rx > sx else -1)
    target_dy = 0 if ry == sy else (1 if ry > sy else -1)

    def dist_to_target(nx, ny):
        return abs(rx - nx) + abs(ry - ny)

    # Try directed move first
    primary = (target_dx, target_dy)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = dist_to_target(nx, ny)
        # tie-break deterministically by direction
        candidates.append((d, 0 if (dx, dy) == primary else 1, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [candidates[0][2], candidates[0][3]]