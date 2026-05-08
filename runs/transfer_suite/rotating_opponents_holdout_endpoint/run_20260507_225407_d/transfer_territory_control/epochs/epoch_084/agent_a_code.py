def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    st = observation.get("self_territory") or []
    for p in st:
        self_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    uc = observation.get("unclaimed_cells") or []
    for p in uc:
        unclaimed.add((int(p[0]), int(p[1])))

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if unclaimed:
        frontier = set()
        for x, y in self_terr:
            for dx, dy in neigh4:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
        targets = sorted(frontier if frontier else unclaimed)
        def dist_to_frontier(cell):
            cx, cy = cell
            best = 10**9
            for x, y in self_terr:
                d = abs(cx - x) + abs(cy - y)
                if d < best:
                    best = d
            return best
        target = min(targets, key=lambda c: (dist_to_frontier(c), c[0], c[1]))
    else:
        target = (ox, oy)

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_score = 10**18
    # Prefer moves that reduce distance to target; avoid obstacles; deterministic tie-break.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = md((nx, ny), target)
        # Slightly prefer moving away from opponent if we're not chasing target well.
        score2 = score + 0.05 * md((nx, ny), (ox, oy))
        if score2 < best_score - 1e-12 or (abs(score2 - best_score) <= 1e-12 and (dx, dy) < best_move):
            best_score = score2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]