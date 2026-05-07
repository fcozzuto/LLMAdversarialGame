def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                sc = - (abs(nx - cx) + abs(ny - cy))
                if sc > best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_exists = ox is not None and oy is not None
    # Pick target: maximize (opp_dist - self_dist), then prefer smaller self_dist, then deterministic tie by coords
    best_t = None
    best_key = (-10**18, 10**9, None)
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry) if opp_exists else sd + 1
        k = (od - sd, -sd, (rx, ry))
        if k > best_key:
            best_key = k
            best_t = (rx, ry)

    tx, ty = best_t
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Evaluate move by predicted race advantage after stepping
            moved_sd = md(nx, ny, tx, ty)
            moved_od = md(ox, oy, tx, ty) if opp_exists else moved_sd + 1
            # Encourage immediate resource capture and slight pathing to reduce distance
            capture = 1000 if (nx, ny) == (tx, ty) else 0
            sc = (moved_od - moved_sd) * 10 + capture - moved_sd
            candidates.append((sc, dx, dy, (nx, ny)))

    # Deterministic fallback if something odd
    if not candidates:
        return [0, 0]

    # Choose best, break ties deterministically by position and move
    candidates.sort(key=lambda t: (-t[0], t[3], t[1], t[2]))
    return [candidates[0][1], candidates[0][2]]