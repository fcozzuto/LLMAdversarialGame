def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
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

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target policy: move toward closest resource if available, else toward opponent to deny.
    if resources:
        target = min(resources, key=lambda r: (manh(sx, sy, r[0], r[1]), r[0], r[1]))
        tx, ty = target[0], target[1]
        # choose move minimizing distance to target
        best = None
        best_score = None
        for dx, dy, nx, ny in legal:
            d = manh(nx, ny, tx, ty)
            score = -d
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy, nx, ny)
        if best is not None:
            return [best[0], best[1]]
    # No resources or fallback: move to reduce distance to opponent or block
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        d_to_opp = manh(nx, ny, ox, oy)
        score = -d_to_opp
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy, nx, ny)
    if best is not None:
        return [best[0], best[1]]
    return [0, 0]