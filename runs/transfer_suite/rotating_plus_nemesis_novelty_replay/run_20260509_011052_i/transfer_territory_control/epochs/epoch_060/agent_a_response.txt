def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    oxp, oyp = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = int(sx), int(sy)
    oxp, oyp = int(oxp), int(oyp)

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cxt, cyt = (w - 1) / 2.0, (h - 1) / 2.0

    frontier = self_terr if self_terr else {(sx, sy)}

    def manh(x, y, a, b):
        return abs(a - x) + abs(b - y)

    def adj_self(x, y):
        return sum((x + dx, y + dy) in self_terr for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)])

    best = (-10**18, 0, 0)
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_self = (nx, ny) in self_terr
        is_opp = (nx, ny) in opp_terr
        is_uncl = (nx, ny) in unclaimed
        d_opp = manh(nx, ny, oxp, oyp)
        d_ctr = abs(nx - cxt) + abs(ny - cyt)
        a_self = adj_self(nx, ny)

        # Prefer central expansion and secure frontier growth; opportunistically capture opponent if adjacent.
        score = 0
        score += (6 if is_opp else 0)
        score += (3 if is_uncl else 0)
        score += (1 if is_self else 0)

        # If stepping into opponent territory, favor being closer to them to reduce escape routes.
        if is_opp:
            score += max(0, 6 - d_opp)

        # Frontier pressure and centrality.
        score += 0.8 * a_self
        score += 0.9 * (7 - d_ctr) / 7.0

        # Avoid wandering into opponent vicinity unless capturing.
        if not is_opp:
            score -= 0.35 * max(0, 6 - d_opp)

        # Deterministic tie-breaker: prefer moves with smaller (dx,dy) lexicographically
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]