def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_r = None
    best_key = None
    for r in resources:
        if not r or len(r) != 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inside(rx, ry):
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive means we are closer
        key = (-adv, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    if best_r is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r

    best_move = (0, 0)
    best_d = None
    best_tieb = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        tieb = (d, abs(ox - nx) + abs(oy - ny), dx, dy)  # deterministic
        if best_d is None or tieb < best_tieb:
            best_d, best_tieb = d, tieb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]