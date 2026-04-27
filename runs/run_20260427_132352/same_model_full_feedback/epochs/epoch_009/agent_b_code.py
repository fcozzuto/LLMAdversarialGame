def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        return [0, 0]

    # Pick best target resource: prefer ones we can reach sooner than opponent.
    tx, ty = None, None
    best = None
    for x, y in resources:
        dm = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        if best is None or (do - dm, -dm, -cheb(ox, oy, x, y)) > best:
            best = (do - dm, -dm, -cheb(ox, oy, x, y))
            tx, ty = x, y

    if tx is None:
        # No resources: drift toward center, but keep steps legal.
        tx, ty = w // 2, h // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Evaluate candidate moves with a deterministic local heuristic.
    best_mv = (0, 0)
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Encourage progress to target and also avoid letting opponent get much closer to the same target.
        opp_to_target = cheb(ox, oy, tx, ty)
        my_gain = (cheb(sx, sy, tx, ty) - d_to_target)
        sc = (my_gain * 10) + (opp_to_target - cheb(ox, oy, tx, ty)) * 0  # keep deterministic
        sc += -d_to_target
        sc += 0.4 * d_opp
        # Small preference to reduce parity conflicts deterministically
        sc += -0.01 * ((nx + ny) & 1)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]