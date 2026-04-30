def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    t = int(observation.get("turn_index", 0) or 0)
    use_alt = (t % 4 == 3)  # deterministic policy switch

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obst_cost(x, y):
        c = 0
        for ix in (-1, 0, 1):
            nx = x + ix
            if nx < 0 or nx >= w:
                continue
            for iy in (-1, 0, 1):
                ny = y + iy
                if ix == 0 and iy == 0:
                    continue
                if 0 <= ny < h and (nx, ny) in obstacles:
                    c += 1
        return c

    oppd = cheb(sx, sy, ox, oy)
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = None

    # Choose a target resource that we are (relatively) closer to; alternate objective occasionally.
    best_target = None
    best_tscore = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        rel = od - sd  # positive means we're closer
        # When close to opponent, slightly reduce contesting; when alternating, prioritize safer/less contested.
        tscore = (rel * 10) - (sd) - (adj_obst_cost(rx, ry) * 2)
        if use_alt:
            tscore = (rel * 6) - (sd * 1.5) + (oppd - od) * 0.5
        if best_tscore is None or tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)

    tx, ty = best_target
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_now = cheb(sx, sy, tx, ty)
        d_next = cheb(nx, ny, tx, ty)
        step_improve = d_now - d_next  # prefer reducing distance

        # Softly avoid stepping into adjacency to obstacles; and avoid being too close to opponent when contesting.
        obst = adj_obst_cost(nx, ny)
        opd_next = cheb(nx, ny, ox, oy)
        opponent_pressure = 0
        if not use_alt and rel > 0:
            opponent_pressure = 0.8 * max(0, 2 - opd_next)  # avoid being within ~1-2 cheb distance

        # Deterministic tie-break by lexicographic preference on (dx