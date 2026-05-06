def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    if not rpos:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        my_min = 10**9
        my_adv_best = -10**9
        my_target = None
        for rx, ry in rpos:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < my_min:
                my_min = myd
            adv = opd - myd  # positive means we are closer than opponent
            if adv > my_adv_best:
                my_adv_best = adv
                my_target = (rx, ry)

        # Prefer gaining advantage, then getting closer, then slight centralization, then reduce being too close to opponent
        oppd_here = cheb(nx, ny, ox, oy)
        center_dist = abs(nx - cx) + abs(ny - cy)
        toward_target = 0
        if my_target:
            toward_target = cheb(nx, ny, my_target[0], my_target[1]) - cheb(sx, sy, my_target[0], my_target[1])

        key = (my_adv_best, -my_min, -toward_target, -oppd_here, -center_dist)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]