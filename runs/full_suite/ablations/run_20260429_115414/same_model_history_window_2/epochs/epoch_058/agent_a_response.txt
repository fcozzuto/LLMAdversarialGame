def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    resset = set()
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
                resset.add((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # If no visible resources, move to increase distance from opponent while keeping mobility.
    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            oppd = cheb((nx, ny), (ox, oy))
            # prefer staying away from edges that could trap us
            edge_pen = min(nx, w - 1 - nx, ny, h - 1 - ny)
            v = oppd * 10 + edge_pen
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Resource race heuristic: prefer moves that make us closer than opponent, and grab if possible.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        selfd = cheb((nx, ny), (sx, sy))
        oppd_self = cheb((nx, ny), (ox, oy))

        # compute best advantage over resources for this step
        adv = -10**18
        for rx, ry in resources:
            if (rx, ry) in blocked:
                continue
            sd = cheb((nx, ny), (rx, ry))
            od = cheb((ox, oy), (rx, ry))
            score = (od - sd) * 1000 - sd  # huge for taking lead, slight tie-break by closeness
            if score > adv:
                adv = score

        grab = 50000 if (nx, ny) in resset else 0

        # obstacle "stickiness": avoid moving into cells with many blocked neighbors
        nb_block = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in blocked:
                nb_block += 1

        # tie-break deterministically: center-ish and smaller opponent distance
        center = -(abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2)))
        v = grab + adv - nb_block * 2 + center - oppd_self * 0.2 - selfd * 0.05

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]