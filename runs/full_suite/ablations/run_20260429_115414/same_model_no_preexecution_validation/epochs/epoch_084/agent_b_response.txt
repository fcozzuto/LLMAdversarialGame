def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Select a target resource likely to be secured: prefer resources closer to us than opponent.
    best_t = None
    best_s = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Deterministic tie-breaker by coordinates.
        s = (do - ds) * 100 - ds - 5 * adj_obst(rx, ry) + (rx - ry) * 0.01
        if best_s is None or s > best_s or (s == best_s and (rx, ry) < best_t):
            best_s = s
            best_t = (rx, ry)

    tx, ty = best_t
    # Choose move that reduces distance to target while avoiding nearby obstacles.
    best_m = (0, 0)
    best_v = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        v = d * 10 + adj_obst(nx, ny) * 3 + (abs((nx - tx)) + abs((ny - ty))) * 0.01
        # Tie-break deterministically.
        if best_v is None or v < best_v or (v == best_v and (dx, dy) < best_m):
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]