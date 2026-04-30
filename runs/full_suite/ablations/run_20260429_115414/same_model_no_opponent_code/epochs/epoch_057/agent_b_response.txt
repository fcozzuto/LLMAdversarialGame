def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        resources = [(w // 2, h // 2)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def nearest_dist(x, y):
        best = 10**9
        for rx, ry in resources:
            d = abs(x - rx) + abs(y - ry)
            if d < best:
                best = d
        return best

    def step_score(x, y, tx, ty):
        # Lower is worse: distance to target resources, then safety from opponent.
        return (abs(x - tx) + abs(y - ty))

    def choose_step(px, py):
        # Predict opponent's likely step deterministically.
        # Target: nearest resource (tie by smaller coord sum).
        tx, ty = min(resources, key=lambda r: (abs(px - r[0]) + abs(py - r[1]), r[0] + r[1], r[1]))
        bestm = (0, 0)
        bestv = 10**18
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny):
                continue
            v = step_score(nx, ny, tx, ty)
            # slight tie-break: prefer moving away from our position to avoid easy capture
            v += 0.01 * (- (abs(nx - sx) + abs(ny - sy)))
            if v < bestv:
                bestv = v
                bestm = (dx, dy)
        return bestm

    # Pick our best move by advantage against predicted opponent progress.
    # Advantage: opponent distance after its predicted step minus our distance after our move.
    best = (0, 0)
    bestv = -10**18
    opp_step = choose_step(ox, oy)
    nox, noy = ox + opp_step[0], oy + opp_step[1]
    my_near = nearest_dist(sx, sy)
    op_near = nearest_dist(nox, noy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = nearest_dist(nx, ny)
        opd = op_near
        adv = opd - myd
        # extra: if resource distances tie, don't collide/approach opponent unnecessarily
        safety = abs(nx - ox) + abs(ny - oy)
        v = 1000 * adv + safety
        # If we're already close, slightly prefer moves that keep approaching (avoid aimless drift)
        v += 0.1 * (-myd)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]