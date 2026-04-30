def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_val = -10**18
    # Deterministic tie-break order by candidate order.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obst:
            continue

        # Choose the resource that is most "winnable" from this next position:
        # maximize (opp_dist - my_dist) and also reduce my_dist to that resource.
        local_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If I'm at/near it, prioritize heavily.
            steal = opd - myd
            val = steal * 100 - myd
            # If both are far, prefer nearer-to-center flow.
            cd = cheb(nx, ny, int(center[0]), int(center[1]))
            val -= cd * 0.01
            if val > local_best:
                local_best = val

        # Additional safety: if opponent is very close, don't drift toward them unless it helps stealing.
        opp_close = cheb(nx, ny, ox, oy)
        opp_pen = 0.0
        if opp_close <= 2:
            opp_pen = (2 - opp_close) * 2.0

        total = local_best - opp_pen
        if total > best_val:
            best_val = total
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]