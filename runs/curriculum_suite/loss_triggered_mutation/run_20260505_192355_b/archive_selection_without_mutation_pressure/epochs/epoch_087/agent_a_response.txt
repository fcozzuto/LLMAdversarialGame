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

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    my_best = None
    best_margin = -10**9
    my_min_dist = 10**9

    for rx, ry in resources:
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        margin = od - md  # positive means we are closer (can reach first)
        if margin > best_margin or (margin == best_margin and md < my_min_dist):
            best_margin = margin
            my_min_dist = md
            my_best = (rx, ry)

    if my_best is None:
        return [0, 0]

    if best_margin >= 1:
        target = my_best  # opportunistically secure a resource we can reach first
    else:
        # Intercept: follow the opponent's nearest resource, but with obstacle-aware step
        opp_nearest = min(resources, key=lambda rr: dist(ox, oy, rr[0], rr[1]))
        target = opp_nearest

    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_d = 10**9
    best_adv = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_to = dist(nx, ny, tx, ty)
        # If intercepting, also try to keep distance to opponent from increasing too much
        d_opp = dist(nx, ny, ox, oy)
        adv = d_opp - dist(sx, sy, ox, oy)
        if d_to < best_d or (d_to == best_d and adv < best_adv) or (d_to == best_d and adv == best_adv and (dx, dy) < best):
            best_d = d_to
            best_adv = adv
            best = (dx, dy)

    return [int(best[0]), int(best[1])]