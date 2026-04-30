def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
    res_set = set(resources)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        on_res = 1 if (nx, ny) in res_set else 0
        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            my_target = mind
        else:
            my_target = 0

        d_opp = cheb(nx, ny, ox, oy)

        opp_pressure = 0
        if resources:
            opp_mind = 10**9
            for rx, ry in resources:
                d = cheb(ox, oy, rx, ry)
                if d < opp_mind:
                    opp_mind = d
            opp_pressure = cheb(ox, oy, nx, ny) - opp_mind

        # Higher is better: capture resource first, then reduce distance to nearest resource,
        # while keeping away from opponent and avoiding moving into their immediate race area.
        score = on_res * 1000 - my_target * 5 + d_opp * 0.3 - opp_pressure * 0.05
        key = (score, -d_opp, -on_res, dx, dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]