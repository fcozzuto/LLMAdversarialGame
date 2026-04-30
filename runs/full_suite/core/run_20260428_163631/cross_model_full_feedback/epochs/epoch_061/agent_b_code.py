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

    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    best_move = None
    best_score = -10**18

    for dx, dy, nx, ny in legal:
        # score: favor getting closer to a resource, but keep distance from opponent
        score = 0
        if resources:
            dist_r = min(md(nx, ny, rx, ry) for rx, ry in resources)
            score -= dist_r  # closer to resource is better
        dist_o = md(nx, ny, ox, oy)
        score += max(0, 4 - dist_o)  # prefer staying away from opponent up to a threshold
        # slight bias toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = md(nx, ny, int(cx), int(cy))
        score -= dist_center * 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]