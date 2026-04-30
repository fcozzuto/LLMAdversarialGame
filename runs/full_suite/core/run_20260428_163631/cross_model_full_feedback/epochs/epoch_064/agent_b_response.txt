def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
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

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Target nearest resource if safe; otherwise approach midpoint between selves with simple rule
    if resources:
        best = None
        best_score = -10**9
        for dx, dy, nx, ny in legal:
            dist_r = min(md(nx, ny, rx, ry) for rx, ry in resources)
            dist_o = md(nx, ny, ox, oy)
            score = -dist_r * 2 - dist_o
            if score > best_score:
                best_score = score
                best = (dx, dy, nx, ny)
        if best is not None:
            return [best[0], best[1]]

    # If no resources or none chosen, move to reduce distance to opponent while staying safe
    best = (0, 0)
    best_score = -10**9
    for dx, dy, nx, ny in legal:
        dist_to_opp = md(nx, ny, ox, oy)
        dist_to_me = md(nx, ny, sx, sy)
        # prefer positions that are closer to us while not enabling opponent to take us
        score = -dist_to_opp + dist_to_me
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]