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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    if resources:
        best = None
        best_sc = -10**18
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            near = -sd
            sc = adv * 50 + near
            if sc > best_sc:
                best_sc = sc
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) if sx < w - 1 else 0, (h - 1) if sy < h - 1 else 0

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_md = (0, 0)
    best_ms = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        curd = cheb(sx, sy, tx, ty)
        self_progress = curd - nsd  # positive is good
        n_od = cheb(ox, oy, tx, ty)
        # If after moving we are not at least as close as opponent, prefer staying off losing grabs.
        contest = (n_od - nsd)
        # Mild wall/obstacle avoidance: penalize neighbors that are blocked/out-of-bounds.
        neigh_block = 0
        for adx, ady in ((-1,0),(1,0),(0,-1),(0,1),(0,0)):
            ax, ay = nx + adx, ny + ady
            if not ok(ax, ay):
                neigh_block += 1
        sc = self_progress * 120 + contest * 40 - nsd - neigh_block * 2
        # If target reachable this move, strongly prefer it.
        if nsd == 0:
            sc += 10**9
        # If opponent could grab immediately on their next step, slightly reduce risk.
        if n_od == 1 and nsd > 1:
            sc -= 200
        if sc > best_ms:
            best_ms = sc
            best_md = (dx, dy)

    return [int(best_md[0]), int(best_md[1])]