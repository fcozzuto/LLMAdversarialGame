def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_t = None
        best_k = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            k = (do - ds) * 10 - ds - 0.01 * (rx + ry)
            if (best_k is None) or (k > best_k) or (k == best_k and (rx, ry) < best_t):
                best_k = k
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    opp_dist = cheb(ox, oy, tx, ty)
    us_dist = cheb(sx, sy, tx, ty)
    aggressive = (us_dist <= opp_dist)

    best_move = (0, 0)
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        score = -d * 3 - (0.1 if aggressive else -0.1) * dop
        score += (opp_dist - cheb(ox, oy, tx, ty)) * 0  # keep deterministic; no side effects
        if not aggressive:
            score += cheb(nx, ny, ox, oy) * 0.2  # drift away when we're behind
        if best_s is None or score > best_s or (score == best_s and (dx, dy) < best_move):
            best_s = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]