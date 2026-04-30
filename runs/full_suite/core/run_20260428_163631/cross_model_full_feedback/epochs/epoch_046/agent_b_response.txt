def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

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

    # If there are resources, move towards the closest resource while also considering distance to opponent
    if resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            d_opp = man((nx, ny), (ox, oy))
            d_res = min(man((nx, ny), r) for r in resources)
            # Prefer positions closer to a resource and farther from opponent modestly
            v = (-d_res, d_opp)
            if best is None or v < bestv:
                best = (dx, dy, nx, ny)
                bestv = v
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move to reduce distance to resource-free nearest point by 1 step if possible,
    # else move away from opponent if collision risk, else stay.
    # Try to move toward empty tile that minimizes distance to any resource spawn linearly.
    target_dx = 0
    target_dy = 0
    if resources:
        # choose neighbor that minimizes distance to closest resource
        best = None
        bestd = None
        for dx, dy, nx, ny in legal:
            d = min(man((nx, ny), r) for r in resources)
            if best is None or d < bestd:
                best = (dx, dy, nx, ny)
                bestd = d
        if best is not None:
            return [best[0], best[1]]

    # If no resources, try to move toward center area while not stepping into opponent's immediate zone too often
    # Simple heuristic: move away from opponent if possible
    best = None
    bestscore = None
    for dx, dy, nx, ny in legal:
        dist_to_opp = man((nx, ny), (ox, oy))
        dist_to_center = abs(nx - w//2) + abs(ny - h//2)
        score = (dist_to_opp, -dist_to_center)
        if best is None or score < bestscore:
            best = (dx, dy, nx, ny)
            bestscore = score
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]