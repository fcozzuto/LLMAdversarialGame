def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (w - 1, h - 1)))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    targets = resources if resources else unclaimed
    if not targets:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def nearest_dist(cell, arr):
        d = 10**9
        for t in arr:
            dd = abs(cell[0] - t[0]) + abs(cell[1] - t[1])
            if dd < d:
                d = dd
        return d

    near_unclaimed = None
    # Only compute once for determinism/efficiency
    nearest_from_start = nearest_dist((sx, sy), targets)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        cell = (nx, ny)

        score = 0.0
        if cell in opp_terr:
            score -= 1.5  # avoid getting dragged back onto their edge
            score += 1.0 / (1 + man(cell, (ox, oy)))
        if cell in unclaimed:
            score += 2.2
        if cell in self_terr:
            score += 0.2

        d_un = nearest_dist(cell, targets)
        # Prefer reducing distance to our chosen target set
        score += 1.6 * (nearest_from_start - d_un)
        # Prefer moving away from opponent position slightly
        score += 0.08 * man(cell, (ox, oy))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]