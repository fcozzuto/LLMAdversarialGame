def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neighbors(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if inb(ax, ay):
                    yield ax, ay

    if unclaimed:
        frontier = []
        if opp:
            for cx, cy in unclaimed:
                for nx, ny in neighbors(cx, cy):
                    if (nx, ny) in opp:
                        frontier.append((cx, cy))
                        break
        targets = frontier if frontier else list(unclaimed)
        tx, ty = min(targets, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    else:
        if opp:
            targets = list(opp)
            tx, ty = min(targets, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
        else:
            return [0, 0]

    raw_dx = 0 if tx == x else (1 if tx > x else -1)
    raw_dy = 0 if ty == y else (1 if ty > y else -1)

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (10**9, raw_dx, raw_dy)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = md(nx, ny, tx, ty)
        if (nx, ny) in unclaimed:
            score -= 2
        elif (nx, ny) in opp:
            score -= 1
        if score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]