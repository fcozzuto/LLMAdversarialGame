def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If we can capture an adjacent resource immediately, do it.
    best_adj = None
    for rx, ry in resources:
        if cheb(sx, sy, rx, ry) == 1:
            if best_adj is None or (rx, ry) < best_adj:
                best_adj = (rx, ry)
    if best_adj is not None:
        tx, ty = best_adj
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    # Choose a target we are likely to reach first; otherwise, minimize opponent-threat.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Hard prefer guaranteed/likely lead; otherwise avoid resources where opponent is equal/closer.
        # Key: (lead_badness, my_distance, opp_distance, tie-break by coordinates)
        lead_badness = 0 if sd < od else (1 if sd == od else 2)
        if lead_badness == 2:
            # Even if we can't lead, still consider if it's much closer to us than opponent.
            threat = (sd - od)
        else:
            threat = 0
        key = (lead_badness + (0.25 * threat), sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    if (sx + dx, sy + dy) in obstacles:
        # Fallback: try axis move that stays unblocked, else stay.
        cand = []
        if dx != 0 and (sx + dx, sy) not in obstacles:
            cand.append((dx, 0))
        if dy != 0 and (sx, sy + dy) not in obstacles:
            cand.append((0, dy))
        if cand:
            # Deterministic: prefer x then y
            dx, dy = cand[0]
        else:
            dx, dy = 0, 0
    return [int(dx), int(dy)]