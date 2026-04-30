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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    # Evaluate each move by the best resource we can contest next.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # If move lands on a resource, prioritize heavily.
        v_move = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            if ds == 0:
                v = 10**9 + (ox != nx or oy != ny)
            else:
                do = cheb(ox, oy, rx, ry)
                # Favor resources where we are closer; slight preference for nearer absolute distance.
                v = (do - ds) * 100 - ds
                # Micro-bias toward breaking ties deterministically by coordinates.
                v += -0.01 * (abs(rx - ox) + abs(ry - oy))
            if v > v_move:
                v_move = v
        # Deterministic tie-break: prefer moves with smaller (abs(dx)+abs(dy)), then lexicographic dx,dy.
        tieb = -(abs(dx) + abs(dy))
        v_total = v_move * 10 + tieb
        if v_total > bestv:
            bestv = v_total
            best = [dx, dy]
    return best