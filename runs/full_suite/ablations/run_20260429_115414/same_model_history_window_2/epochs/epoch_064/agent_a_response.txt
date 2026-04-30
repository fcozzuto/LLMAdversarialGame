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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = (0, 0)
    best_val = -10**18

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_best = 10**9
            my_dist_center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
            val = -0.01 * my_dist_center
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                my_best = myd if myd < my_best else my_best
                # Prefer states where we are closer than opponent, strongly.
                val += (opd - myd) * 1.0 / (1.0 + myd)
                # Encourage immediate pickup/near-term.
                if myd == 0:
                    val += 1000.0
                else:
                    val += 5.0 / (1.0 + myd)
            if val > best_val:
                best_val = val
                best = (dx, dy)
    else:
        # No visible resources: move to improve mobility and drift toward opponent's side.
        tx = w - 1 if ox < (w - 1) / 2.0 else 0
        ty = h - 1 if oy < (h - 1) / 2.0 else 0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            val = -d
            if val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]