def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, head to opposite corner from opponent
    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Evaluate candidate moves by (min self distance to resources) and (min opp distance),
    # giving advantage if we can reduce our lead or increase opponent's disadvantage.
    best = None  # (score, dx, dy)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                nx, ny = sx, sy  # engine would keep us; mirror it
            # Distances from next positions
            self_best = 10**9
            opp_best = 10**9
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                if d1 < self_best: self_best = d1
                d2 = cheb(ox, oy, rx, ry)
                if d2 < opp_best: opp_best = d2

            # Score: minimize our distance; maximize opponent being farther
            # Also add mild penalty for moving away from current nearest resource (stability).
            cur_self_best = 10**9
            for rx, ry in resources:
                d = cheb(sx, sy, rx, ry)
                if d < cur_self_best: cur_self_best = d

            score = (self_best * 3) - (opp_best * 2) + (self_best - cur_self_best)
            # Deterministic tie-break: prefer moves that reduce dx,dy magnitude from center toward target
            cand = (score, dx, dy)
            if best is None or cand < best:
                best = cand

    return [int(best[1]), int(best[2])]