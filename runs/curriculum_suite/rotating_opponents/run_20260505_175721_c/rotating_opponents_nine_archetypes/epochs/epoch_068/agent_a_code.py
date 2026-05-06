def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        def man(a, b, c, d):
            a -= c
            if a < 0: a = -a
            b -= d
            if b < 0: b = -b
            return a + b

        best_key = None
        tx, ty = resources[0]
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we can secure (sd <= od), then closest.
            # Otherwise contest by minimizing (od - sd), then reduce sd.
            if sd <= od:
                key = (0, sd, -od, rx, ry)
            else:
                key = (1, od - sd, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                tx, ty = rx, ry

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_ok(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        opp_dist = abs(nx - ox) + abs(ny - oy)
        # Small secondary terms to avoid dithering and keep separation from opponent.
        val = (dist, -opp_dist, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]