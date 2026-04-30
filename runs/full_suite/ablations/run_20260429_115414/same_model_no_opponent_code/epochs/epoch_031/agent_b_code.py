def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    target = None
    best = None
    for tx, ty in resources:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - md
        key = (adv, -md, -cheb(ox, oy, sx, sy), tx, ty)
        if best is None or key > best:
            best = key
            target = (tx, ty)

    # If no resources, move to maximize distance from opponent.
    if target is None:
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            nd = cheb(nx, ny, ox, oy)
            key = (nd, -cheb(nx, ny, sx, sy), -dx, -dy)
            if best_score is None or key > best_score:
                best_score = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = target
    myd = cheb(sx, sy, tx, ty)
    opd = cheb(ox, oy, tx, ty)

    # Decide strategy: go for target; if behind, prioritize blocking by moving closer to target anyway.
    go_for = True
    if myd > opd:
        go_for = True

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd_my = cheb(nx, ny, tx, ty)
        nd_op = cheb(ox, oy, tx, ty)
        new_adv = nd_op - nd_my
        nd_to_opp = cheb(nx, ny, ox, oy)
        # Favor: maximize new_adv; then minimize nd_my; then maximize separation from opponent; then prefer staying closer to target direction.
        key = (new_adv if go_for else -new_adv,
               -nd_my,
               nd_to_opp,
               -abs(tx - nx) - abs(ty - ny),
               -dx, -dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]