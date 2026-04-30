def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def best_value(px, py):
        if not resources:
            dc = cheb(px, py, int(cx), int(cy))
            return -dc
        bestv = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            center = cheb(rx, ry, int(cx), int(cy))
            # Prefer being closer than opponent; also prefer closer overall and more central resources.
            v = (do - ds) * 20 - ds - center * 0.1
            if v > bestv:
                bestv = v
        return bestv

    best_move = [0, 0]
    best_score = -10**18
    # Deterministic tie-break: iterate in fixed order, keep first best.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = best_value(nx, ny)
        # Small penalty for being too close to opponent unless contested by a closer resource.
        score -= cheb(nx, ny, ox, oy) * 0.01
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all candidate moves invalid (should be rare), stay put.
    return [int(best_move[0]), int(best_move[1])]