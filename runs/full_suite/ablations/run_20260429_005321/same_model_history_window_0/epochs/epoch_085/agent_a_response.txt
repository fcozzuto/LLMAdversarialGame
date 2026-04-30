def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        # fallback: head toward opponent corner-ish to force interaction
        tx, ty = (w - 1, h - 1) if (sx < w//2) else (0, 0)
    else:
        best = None
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            # prefer resources we can reach sooner; slight tie-break toward opponent being farther
            key = (ds - do, ds, -rx, -ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    # candidate moves: prefer direct toward target, then other directions deterministically
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx; ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = abs(tx - nx) + abs(ty - ny)
                # primary: closer to target, secondary: reduce distance to opponent to contest, tertiary: lexicographic
                opp_dist = abs(ox - nx) + abs(oy - ny)
                candidates.append((dist, -opp_dist, dx, dy))
    if not candidates:
        return [0, 0]
    # Sort candidates deterministically
    candidates.sort()
    # If direct step is available, ensure it's first unless it leads strictly worse
    for dist, opp_dist, dx, dy in candidates:
        if dx == dx0 and dy == dy0:
            return [dx, dy]
    return [candidates[0][2], candidates[0][3]]