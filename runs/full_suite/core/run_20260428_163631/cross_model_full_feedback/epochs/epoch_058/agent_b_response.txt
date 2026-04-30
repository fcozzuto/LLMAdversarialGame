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

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If resources exist, go to nearest resource, else move to maximize distance from opponent
    if resources:
        best = None
        best_score = -10**9
        for dx, dy, nx, ny in legal:
            nxt = (nx, ny)
            # distance to nearest resource
            d_res = min(dist(nxt, r) for r in resources)
            # distance to opponent (maximize moving away)
            d_opp = dist(nxt, (ox, oy))
            score = -d_res * 2 + d_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # No resources or no good resource path: move to maximize distance from opponent, with a bias to stay close to center
    best = None
    bestv = -10**9
    for dx, dy, nx, ny in legal:
        v = dist((nx, ny), (ox, oy))
        # prefer staying closer to center to avoid edge cases
        center_dist = dist((nx, ny), (w//2, h//2))
        v -= center_dist * 0.0  # no real effect, kept for deterministic tweak
        if v > bestv:
            bestv = v
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]