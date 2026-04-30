def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if resources:
        # Pick resource where we have the best distance advantage over the opponent.
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer advantage; tie-break toward smaller self distance deterministically.
            val = (do - ds) * 1000 - ds
            if best is None or val > best[0] or (val == best[0] and ds < best[1]):
                best = (val, ds, rx, ry)
        _, _, tx, ty = best
    else:
        # No visible resources: move toward opponent side to intercept.
        tx, ty = w - 1 - sx, h - 1 - sy

    # Choose move that minimizes distance to target; but if opponent is close, maximize distance from them.
    cur_best = None
    best_move = [0, 0]
    opp_close = cheb(sx, sy, ox, oy) <= 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dt = cheb(nx, ny, tx, ty)
        da = cheb(nx, ny, ox, oy)
        if opp_close:
            # Primary: keep away; Secondary: still progress to target.
            val = (da * 1000) - dt
        else:
            # Primary: progress to target.
            val = (-dt * 1000) - da
        # Deterministic tie-break: lower dx, then lower dy.
        if cur_best is None or val > cur_best or (val == cur_best and (dx, dy) < (best_move[0], best_move[1])):
            cur_best = val
            best_move = [dx, dy]

    return best_move