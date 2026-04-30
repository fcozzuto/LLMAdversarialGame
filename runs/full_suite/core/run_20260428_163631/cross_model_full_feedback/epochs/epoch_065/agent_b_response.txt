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
            x = int(p[0]); y = int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
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

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Simple deterministic policy:
    # 1) If a resource reachable in one step (including current), move toward closest one.
    # 2) Else move toward the opponent's position using greedy approach, preferring horizontal if closer.
    if resources:
        best = None
        best_score = 10**9
        for dx, dy, nx, ny in legal:
            # distance to closest resource from candidate
            dist_r = min(md(nx, ny, rx, ry) for rx, ry in resources)
            dist_o = md(nx, ny, ox, oy)
            score = dist_r * 2 + dist_o  # prioritize resource proximity
            if score < best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # Otherwise head toward opponent
    # choose step that reduces Manhattan distance to opponent
    best = (0,0)
    best_dist = md(sx, sy, ox, oy)
    for dx, dy, nx, ny in legal:
        d = md(nx, ny, ox, oy)
        if d < best_dist:
            best_dist = d
            best = (dx, dy)
    return [best[0], best[1]]