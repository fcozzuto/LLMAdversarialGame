def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("avoid" in role_s) or ("runner" in role_s) or ("flee" in role_s)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Prefer evader to head to a corner that is farthest from pursuer; deterministic tie-break by (x+y, x)
    far_corner = None
    best_corner_dist = -1
    for cx, cy in corners:
        d = cheb(cx, cy)
        key = (d, -(cx + cy), -cx)
        if d > best_corner_dist:
            best_corner_dist = d
            far_corner = (cx, cy)
        elif d == best_corner_dist:
            if key > (best_corner_dist, float("-inf"), float("-inf")):
                far_corner = (cx, cy)
    fx, fy = far_corner if far_corner is not None else (0, 0)

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        dist = cheb(nx, ny)
        # Evader: maximize distance; also pull toward chosen far corner while maintaining distance
        if is_evader:
            val = (dist, -abs(nx - fx) - abs(ny - fy), -abs(nx - sx) - abs(ny - sy))
        else:
            # Pursuer: minimize distance; break ties by moving toward opponent and away from far corner
            val = (-dist, -(abs(nx - ox) + abs(ny - oy)), abs(nx - fx) + abs(ny - fy))
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]