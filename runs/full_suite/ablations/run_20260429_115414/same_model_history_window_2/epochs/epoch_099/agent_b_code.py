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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Choose target deterministically: maximize (opp_dist - self_dist); then minimize self_dist; then position.
    best_target = None
    best_adv = None
    best_selfd = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if best_target is None or adv > best_adv or (adv == best_adv and (sd < best_selfd or (sd == best_selfd and (rx < best_target[0] or (rx == best_target[0] and ry < best_target[1]))))):
            best_target = (rx, ry)
            best_adv = adv
            best_selfd = sd

    # If no resources, deterministically drift toward opponent-denial: closer to opponent in Chebyshev; otherwise toward center.
    if best_target is None:
        tx, ty = (w // 2, h // 2)
        best = None
        best_val = None
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, ox, oy)
            if v < -1e12: pass
            if best is None or v > best_val or (v == best_val and cheb(nx, ny, tx, ty) < cheb(best[2], best[3], tx, ty)):
                best = (dx, dy, nx, ny)
                best_val = v
        return [int(best[0]), int(best[1])]

    rx, ry = best_target

    # Pick the move that improves our advantage toward the target; tie-break by safety (avoid proximity to opponent) then determinism.
    best_move = None
    best_tuple = None
    for dx, dy, nx, ny in legal:
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # higher is better
        # For tie-breaking: closer to target better; then farther from opponent better (less interference), then lexicographic dx,dy.
        oppd = cheb(nx, ny, ox, oy)
        tup = (adv, -sd, oppd, -abs(dx), -abs(dy), dx, dy)
        if best_tuple is None or tup > best_tuple:
            best_tuple = tup
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]