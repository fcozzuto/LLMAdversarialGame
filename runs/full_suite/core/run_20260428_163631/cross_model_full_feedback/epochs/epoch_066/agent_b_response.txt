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

    # Prefer staying close to resources, then approach opponent if needed
    best = None
    best_score = None

    for dx, dy, nx, ny in legal:
        score = 0
        # distance to nearest resource
        if resources:
            dist_r = min(md(nx, ny, rx, ry) for rx, ry in resources)
            score -= dist_r  # closer to resource better
        else:
            score += 0
        # distance to opponent (to block or pressure)
        dist_o = md(nx, ny, ox, oy)
        score -= max(0, 2 - dist_o)  # encourage closer if not too far
        # proximity to obstacles heuristic: avoid stepping adjacent to many obstacles
        adj = 0
        for ax in (nx-1, nx, nx+1):
            for ay in (ny-1, ny, ny+1):
                if (ax, ay) in obstacles:
                    adj += 1
        score -= adj * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy, nx, ny)

    if best is None:
        return [0, 0]
    dx, dy, _, _ = best
    return [dx, dy]