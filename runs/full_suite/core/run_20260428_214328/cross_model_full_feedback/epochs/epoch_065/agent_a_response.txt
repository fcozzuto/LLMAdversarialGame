def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_move_towards(tx, ty):
        best = (0, 0)
        best_key = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inside(nx, ny) or (nx, ny) in obstacles:
                    continue
                myd = cheb(nx, ny, tx, ty)
                od = cheb(ox, oy, tx, ty)
                key = (myd, od, abs(nx - ox) + abs(ny - oy), (dx == 0 and dy == 0))
                if best_key is None or key < best_key:
                    best_key = key
                    best = (dx, dy)
        return [best[0], best[1]]

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer positions we can reach strictly earlier; then closest among those.
            # If tied, prefer those closer to opponent (to avoid losing tempo later).
            key = (-(od - myd), myd, -od, cheb(sx, sy, rx, ry))
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        # Move towards chosen resource, but re-evaluate local safety with opponent tempo.
        return best_move_towards(best_r[0], best_r[1])

    # No visible resources: deterministically drift toward center while keeping away from obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    return best_move_towards(cx, cy)