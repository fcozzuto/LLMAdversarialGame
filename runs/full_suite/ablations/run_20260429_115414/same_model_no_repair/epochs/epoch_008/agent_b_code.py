def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if resources:
        tx, ty = None, None
        best = None
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd  # prefer resources opponent is farther from
            # secondary: prefer smaller myd, then closer to center for stability
            key = (adv, -myd, -(abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)), -rx, -ry)
            if best is None or key > best:
                best = key
                tx, ty = rx, ry
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = None
    cur_dto = cheb(sx, sy, tx, ty)
    cur_dop = cheb(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dto = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)

        # Encourage getting closer to target, discourage approaching opponent, avoid stepping into choke points lightly.
        step_to = cur_dto - dto  # positive if closer
        step_op = dop - cur_dop  # positive if farther
        res_near = -man(nx, ny, tx, ty)  # deterministic tie-break

        score = (10 * step_to) + (6 * step_op) + (2 * (1 if dto == 0 else 0)) + (0.1 * res_near)
        tie = (dto, -dop, dx, dy, nx, ny)
        cand = (score, -tie[0], tie[1], tie[2], tie[3], tie[4], tie[5])

        if best_score is None or cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]