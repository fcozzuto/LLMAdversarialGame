def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)
    my = (int(sx), int(sy))
    opp = (int(ox), int(oy))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = -10**9
    tleft = observation.get("turns_remaining", 0)
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = cheb(my, (rx, ry))
        od = cheb(opp, (rx, ry))
        # Prefer resources we can reach earlier; if equal, prefer those closer to center of our path.
        reach_adv = od - md  # positive if we are earlier
        # Denier: avoid chasing resources far behind opponent.
        if reach_adv < -2:
            continue
        center_bias = 3.5 - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)) * 0.35
        # Contest near opponent row: if opponent is near that resource, it's also high contest value.
        contest = 0.4 * (10 - min(10, cheb(opp, (rx, ry))))
        # Slight preference to reduce our distance to opponent (cutting denier lines).
        swing = 0.15 * (cheb(my, opp) - cheb((rx, ry), opp))
        # If many turns left, favor farther but favorable contests a bit more.
        time_scale = 1.0 + 0.25 * min(1.0, tleft / 40.0)
        val = (2.2 * reach_adv + 0.9 * max(0, reach_adv) + contest + center_bias + swing) * time_scale - 0.05 * md
        if val > best_val:
            best_val = val
            best = (rx, ry)

    if best is None:
        # Fallback: move to reduce distance to nearest resource (deterministic scan).
        nearest = None
        nd = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in obstacles:
                continue
            d = cheb(my, (rx, ry))
            if d < nd:
                nd = d
                nearest = (rx, ry)
        best = nearest if nearest is not None else my

    tx, ty = best
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        md2 = cheb((nx, ny), (tx, ty))
        od2 = cheb(opp, (tx, ty))
        # Score move by improving our reach advantage; also keep moving generally toward target.
        reach_adv2 = od2 - md2
        toward = cheb((nx, ny), (tx, ty))
        # Avoid blundering into opponent by mild penalty on closeness after move.
        opp_close = cheb((nx, ny), opp)
        score = 3.0 * reach_adv2 + (-0.06) * toward + (-0.10) * opp_close
        # If already on resource, stay put (resource collection assumed by engine).
        if (nx, ny) == (tx, ty):
            score = 10**6
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]