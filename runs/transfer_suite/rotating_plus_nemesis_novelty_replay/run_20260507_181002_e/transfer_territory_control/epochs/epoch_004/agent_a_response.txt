def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not unclaimed:
        unclaimed = set(resources)

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    frontier = set()
    if oppT:
        for (x, y) in oppT:
            for dx, dy in adj8:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in oppT:
                    frontier.add((nx, ny))
    if frontier:
        targets = list(frontier)
    else:
        targets = list(unclaimed) if unclaimed else []

    if targets:
        target = min(targets, key=lambda t: dist((sx, sy), t))
    else:
        target = (ox, oy)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        s = -dist((nx, ny), target)
        if (nx, ny) in oppT:
            s += 2.5
        elif (nx, ny) in unclaimed:
            s += 0.9
        elif (nx, ny) in selfT:
            s -= 0.3
        # small nudge to avoid just standing
        s -= 0.05 * (1 if (dx != 0 or dy != 0) else 0)
        if s > best_score:
            best_score = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]