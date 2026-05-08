def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = list(observation.get("resources") or [])
    if not resources:
        rc = observation.get("remaining_resource_count")
        if rc is None:
            resources = []

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    center = (w // 2, h // 2)

    def best_dist(x, y):
        if resources:
            bd = 10**9
            for p in resources:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    rx, ry = int(p[0]), int(p[1])
                    d = abs(x - rx) + abs(y - ry)
                    if d < bd:
                        bd = d
            return bd
        return abs(x - center[0]) + abs(y - center[1])

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = best_dist(nx, ny)
        score = -d
        if (nx, ny) in selfT:
            score += 3
        if (nx, ny) in oppT:
            score -= 8
        if max(abs(nx - ox), abs(ny - oy)) <= 1:
            score -= 6
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]