def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    if not self_terr:
        self_terr = {(sx, sy)}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_self(x, y):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in self_terr:
                c += 1
        return c

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Find a few nearest unclaimed cells to help direction (bounded for speed/determinism)
    targets = list(unclaimed) if unclaimed else []
    if targets:
        targets.sort(key=lambda p: (man(p[0], p[1], ox, oy), man(sx, sy, p[0], p[1]), p[0], p[1]))
        targets = targets[:8]
    else:
        targets = [(ox, oy)]

    best = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0
        score += 3.5 if (nx, ny) in opp_terr else 0.0  # flipping on entry is strong
        score += 2.0 if (nx, ny) in unclaimed else 0.0
        score += 0.5 if (nx, ny) in self_terr else 0.0
        score += 0.25 * adj_self(nx, ny)

        # Directional bias: move toward unclaimed closer to opponent, but avoid giving up distance if unclaimed absent
        cur_best = min(man(sx, sy, px, py) for px, py in targets) if targets else man(sx, sy, ox, oy)
        new_best = min(man(nx, ny, px, py) for px, py in targets) if targets else man(nx, ny, ox, oy)
        score += 1.2 * (cur_best - new_best)

        # Subtle pressure: prefer decreasing distance to opponent (even if not capturing immediately)
        score += 0.05 * (man(sx, sy, ox, oy) - man(nx, ny, ox, oy))

        if score > best_score:
            best_score = score
            best = [dx, dy]
    return [int(best[0]), int(best[1])]