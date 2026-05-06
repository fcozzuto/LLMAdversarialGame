def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                rx, ry = int(q[0]), int(q[1])
                if inb(rx, ry) and (rx, ry) not in blocked:
                    rpos.append((rx, ry))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in blocked:
                rpos.append((rx, ry))
    if not rpos:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        best_adv = -10**9
        best_res = None
        for rx, ry in rpos:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive => we arrive no later than opponent
            if adv > best_adv:
                best_adv = adv
                best_res = (rx, ry)

        rx, ry = best_res
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Favor states where we can win a resource race; break ties by closer-to-resource and farther-from-opponent.
        dist_center = abs(nx - cx) + abs(ny - cy)
        key = (-best_adv, sd - od, sd, dist_center, (nx - ox) + (ny - oy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]