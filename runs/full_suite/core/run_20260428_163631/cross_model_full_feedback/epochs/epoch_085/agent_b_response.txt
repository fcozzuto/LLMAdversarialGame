def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    op = (ox, oy)

    def best_resource_for(pos):
        if not resources:
            return None, 10**9
        m = None
        md = 10**9
        for r in resources:
            d = dist(pos, r)
            if d < md:
                md = d
                m = r
        return m, md

    # Try to approach closest resource if it is not blocked by obstacle
    res, dres = best_resource_for(my)
    if res is not None:
        dx = res[0] - sx
        dy = res[1] - sy
        # clamp to -1,0,1
        dx = max(-1, min(1, dx))
        dy = max(-1, min(1, dy))
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            # ensure not stepping onto opponent to avoid collision penalty
            if (nx, ny) != op:
                return [dx, dy]

    # If cannot safely approach resource, move to maximize distance from opponent deterministically
    best = None
    bestd = -1
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = dist((nx, ny), op)
        if d > bestd:
            bestd = d
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # Fallback: stay
    return [0, 0]