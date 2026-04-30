def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) if sx < w // 2 else 0, (h - 1) if sy < h // 2 else 0
        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty)
            if best_val is None or v < best_val:
                best_val = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Target most contestable resource: maximize (opp_dist - my_dist).
    best_t = resources[0]
    best_adv = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        if best_adv is None or adv > best_adv or (adv == best_adv and (myd < cheb(sx, sy, best_t[0], best_t[1]))):
            best_adv = adv
            best_t = (tx, ty)

    tx, ty = best_t
    # Choose move that improves my distance while also not letting opponent get too close relatively.
    best_move = (0, 0)
    best_score = None
    my0 = cheb(sx, sy, tx, ty)
    op0 = cheb(ox, oy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Higher is better: reduce myd, increase (opd - myd), and avoid stagnation.
        score = (opd - myd) * 1000 - myd - (1 if myd == my0 else 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]