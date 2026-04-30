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
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if inb(x, y):
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if inb(x, y) and (x, y) not in obstacles:
            resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target nearest resource while avoiding opponent proximity
    if resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            d = min(man((nx, ny), r) for r in resources)
            dist_to_opp = max(abs(nx - ox), abs(ny - oy))
            val = d - dist_to_opp  # prefer closer to resource, farther from opponent
            if best is None or val < bestv:
                best = (dx, dy, nx, ny)
                bestv = val
        if best is not None:
            return [best[0], best[1]]

    # If no resources visible, move to maximize distance from opponent and stay near center
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        dist_opp = max(abs(nx - ox), abs(ny - oy))
        dist_center = max(abs(nx - (w-1)/2), abs(ny - (h-1)/2))
        # deterministic tie-breaker: prefer staying closer to center
        val = (dist_opp * 2) + dist_center
        if best is None or val > bestv:
            best = (dx, dy, nx, ny)
            bestv = val
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]