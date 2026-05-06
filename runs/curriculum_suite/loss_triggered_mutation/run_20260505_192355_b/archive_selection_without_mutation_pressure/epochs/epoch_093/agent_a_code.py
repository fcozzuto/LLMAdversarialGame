def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_margin = -10**9
    best_my_dist = 10**9

    opp_closest = None
    opp_dist_min = 10**9

    for rx, ry in resources:
        md = mdist(sx, sy, rx, ry)
        od = mdist(ox, oy, rx, ry)
        margin = od - md
        if margin > best_margin or (margin == best_margin and md < best_my_dist):
            best_margin = margin
            best_my_dist = md
            best = (rx, ry)
        if od < opp_dist_min:
            opp_dist_min = od
            opp_closest = (rx, ry)

    target = best if best_margin >= 0 else opp_closest
    if target is None:
        return [0, 0]
    tx, ty = target

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    return [dx, dy]