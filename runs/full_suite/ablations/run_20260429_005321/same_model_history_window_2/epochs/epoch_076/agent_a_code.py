def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        bestm = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < bestm):
                bestv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # Pick a target where we have advantage; otherwise pick highest potential.
    best_target = None
    best_tscore = -10**9
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        tscore = (od - md)  # positive means we're closer
        if (rx, ry) == (sx, sy):
            tscore += 1000
        # slight bias to nearer targets to break ties deterministically
        tscore += -0.01 * md
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)

    tx, ty = best_target
    cur_d = cheb(sx, sy, tx, ty)

    bestm = (0, 0)
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        mdiff = cur_d - nd  # progress toward target
        opp_close = cheb(nx, ny, ox, oy)
        hit = 1 if (nx, ny) == (tx, ty) else 0
        # If we're not currently advantaged for the target, slightly prefer moves that deny opponent proximity.
        my_to_target = cheb(sx, sy, tx, ty)
        op_to_target = cheb(ox, oy, tx, ty)
        deny = 0.0
        if my_to_target > op_to_target:
            deny = -0.02 * cheb(nx, ny, ox, oy)
        v = 5.0 * mdiff + 20.0 * hit - 0.005 * nd + deny - 0.001 * opp_close
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]