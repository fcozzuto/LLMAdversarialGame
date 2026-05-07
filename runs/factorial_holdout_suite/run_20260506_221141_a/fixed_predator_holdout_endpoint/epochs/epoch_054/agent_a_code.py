def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
        except Exception:
            pass
    if not resources:
        return [0, 0]

    def kd(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    def center_bias(x, y):
        cx, cy = w // 2, h // 2
        return -(abs(x - cx) + abs(y - cy))

    # Pick a target with maximum advantage; if none positive, pick best overall.
    best_t = resources[0]
    best_s = -10**18
    for t in resources:
        sd = kd((sx, sy), t)
        od = kd((ox, oy), t)
        adv = od - sd
        s = adv * 1000 - sd + center_bias(t[0], t[1])
        if s > best_s:
            best_s = s
            best_t = t
    target = best_t

    # Choose move that maximizes immediate improvement toward target and keeps away from obstacles.
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    tx, ty = target
    cur_d = kd((sx, sy), target)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nd = kd((nx, ny), target)
        progress = cur_d - nd
        # Deny factor: prefer moves that keep opponent far from the same target (in case of tie).
        opp_d = kd((ox, oy), target)
        self_d = nd
        deny = opp_d - self_d
        # Slightly penalize stepping adjacent to obstacles (fragility).
        adj_pen = 0
        for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs:
                adj_pen += 1
        val = progress * 2000 + deny * 10 + center_bias(nx, ny) - adj_pen * 3 - nd
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]