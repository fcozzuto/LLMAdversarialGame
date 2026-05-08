def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    unclaimed = []
    for c in (observation.get("unclaimed_cells") or []):
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    opp_t = set()
    for c in (observation.get("opponent_territory") or []):
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    self_t = set()
    for c in (observation.get("self_territory") or []):
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                self_t.add((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = unclaimed
    if not targets:
        targets = []
        for p in (observation.get("resources") or []):
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    targets.append((x, y))
        if not targets:
            targets = [(sx, sy)]

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        min_d = min(dist((nx, ny), t) for t in targets)
        score = -min_d
        if (nx, ny) in unclaimed:
            score += 50
        if (nx, ny) in self_t:
            score += 2
        if (nx, ny) in opp_t:
            score -= 30
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best