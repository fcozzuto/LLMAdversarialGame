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
            if inb(x, y):
                obstacles.add((x, y))

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
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    me = (sx, sy); opp = (ox, oy)

    # Primary: move toward closest resource, prioritizing positions that increase distance from opponent
    if resources:
        best = None
        best_score = -10**9
        for dx, dy, nx, ny in legal:
            nxt = (nx, ny)
            d_me = dist(nxt, min(resources, key=lambda r: dist(nxt, r)))
            d_opp = dist(nxt, opp)
            # score: closer to resource and as far as possible from opponent
            score = -d_me + (d_opp)
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move to maximize distance from opponent
    best = None
    best_score = -10**9
    for dx, dy, nx, ny in legal:
        d = dist((nx, ny), opp)
        if d > best_score:
            best_score = d
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]