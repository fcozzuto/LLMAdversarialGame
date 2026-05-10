def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "pursuer").lower()
    self_pursuer = "pursuer" in role

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a deterministic corner to bias evasion (or pursuit fallback)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if corners:
        # For evader: farthest-from-pursuer corner; for pursuer: closest corner as fallback
        if self_pursuer:
            target_corner = min(corners, key=lambda c: man(c[0], c[1], sx, sy))
        else:
            target_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
    else:
        target_corner = (w - 1, h - 1)

    best = None
    bestv = None
    # Deterministic tie-break: fixed move ordering by cand as given
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if self_pursuer:
            # Pursuer: minimize distance to opponent; if tied, avoid dead-ends by favoring moves with better space (sum of legal neighbors)
            d = man(nx, ny, ox, oy)
            if d == 0:
                v = -10**9
            else:
                neigh = 0
                for ddx, ddy in cand:
                    tx, ty = nx + ddx, ny + ddy
                    if legal(tx, ty):
                        neigh += 1
                # also lightly prefer moving generally toward target_corner (stabilize policy)
                v = -(100 * d + 2 * (man(nx, ny, target_corner[0], target_corner[1])) - neigh)
        else:
            # Evader: maximize distance from pursuer; if tied, go toward farthest corner bias; if still tied, prefer more mobility
            d = man(nx, ny, ox, oy)
            neigh = 0
            for ddx, ddy in cand:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    neigh += 1
            v = 100 * d - 2 * man(nx, ny, target_corner[0], target_corner[1]) + neigh
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]