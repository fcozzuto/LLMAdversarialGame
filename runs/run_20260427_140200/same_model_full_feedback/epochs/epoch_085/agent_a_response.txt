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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = (10**9, 10**9, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            v = (d, abs(nx - ox) + abs(ny - oy), -dx - dy)
            if best is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose a "winning" resource target, then step toward it.
    best_target = None
    best_tv = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer: myd much smaller than opd; then closer myd; then higher priority for central-ish.
        center = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        tv = (-(opd - myd), myd, center, rx, ry)
        if best_target is None or tv < best_tv:
            best_target = (rx, ry)
            best_tv = tv

    tx, ty = best_target
    best = [0, 0]
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd_next = cheb(nx, ny, tx, ty)
        opd_next = cheb(ox, oy, tx, ty)
        # If it can't keep the lead, still progress; also lightly discourage moving into "losing" parity.
        lead = opd_next - myd_next
        dist_to_res = myd_next
        opp_dist_after = cheb(nx, ny, ox, oy)
        v = (-lead, dist_to_res, opp_dist_after, dx, dy)
        if bestv is None or v < bestv:
            bestv = v
            best = [dx, dy]
    return best