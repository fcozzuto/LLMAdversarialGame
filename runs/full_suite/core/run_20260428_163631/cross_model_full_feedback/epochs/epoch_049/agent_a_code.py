def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    # If standing on a resource, stay to secure it deterministically.
    if (sx, sy) in obstacles:
        return [0, 0]
    if resources and (sx, sy) in set(resources):
        return [0, 0]

    opp = (ox, oy)
    resset = set(resources)

    best = None
    best_key = None
    for dx, dy, nx, ny in legal:
        pos = (nx, ny)
        d_op = cheb(pos, opp)  # Chebyshev distance allows diagonal step parity.
        if resources:
            # Aim for closest resource; if multiple, prefer ones with better safety margin.
            d_to = 10**9
            for r in resources:
                d = cheb(pos, r)
                if d < d_to:
                    d_to = d
            # Slightly reward being on/adjacent to a resource.
            res_bonus = -100 if pos in resset else (-20 if d_to <= 1 else 0)
            # Key: minimize resource distance, maximize distance from opponent, then prefer staying closer to center.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_dist = abs(nx - cx) + abs(ny - cy)
            key = (d_to, -d_op, center_dist, res_bonus)
        else:
            # No resources: go toward center but keep away from opponent.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_dist = abs(nx - cx) + abs(ny - cy)
            key = (center_dist, -d_op, 0, 0)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]