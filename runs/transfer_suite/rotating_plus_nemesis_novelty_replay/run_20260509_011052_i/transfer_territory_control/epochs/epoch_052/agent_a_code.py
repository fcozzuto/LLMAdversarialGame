def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = list(observation.get("unclaimed_cells", []) or [])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**9
        d = abs(x - sx) + abs(y - sy)
        aopp = adj_count(x, y, opp_terr)
        aown = adj_count(x, y, self_terr)
        # Prefer boundary points next to opponent territory, and unclaimed far from our own.
        # Also bias toward reducing distance to opponent.
        return 30 * aopp - 10 * aown - d - 0.2 * (abs(x - ox) + abs(y - oy))

    # Choose target: best unclaimed; if none, use opponent territory cells near frontier.
    target = None
    best = -10**18
    if unclaimed:
        for x, y in unclaimed:
            sc = cell_score(int(x), int(y))
            if sc > best or (sc == best and (int(x), int(y)) < target):
                best = sc
                target = (int(x), int(y))
    if target is None:
        opp_candidates = list(opp_terr) if opp_terr else [(int(ox), int(oy))]
        for x, y in opp_candidates:
            # Move toward cells that increase adjacency to opp even more.
            sc = 20 * adj_count(x, y, opp_terr) - abs(x - sx) - abs(y - sy)
            if sc > best or (sc == best and (x, y) < target):
                best = sc
                target = (x, y)

    # Convert target into a move (greedy one-step) maximizing local progress and flip likelihood.
    tx, ty = target
    best_move = (0, 0)
    best_ms = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ms = - (abs(nx - tx) + abs(ny - ty))
        ms += 6 * adj_count(nx, ny, opp_terr)
        if (nx, ny) in opp_terr:
            ms += 25  # likely immediate flip on entry
        ms -= 3 * adj_count(nx, ny, self_terr)
        # Small tie-break: deterministic preference toward staying closer to opponent.
        ms -= 0.05 * (abs(nx - ox) + abs(ny - oy))
        if ms > best_ms or (ms == best_ms and (dx, dy) < best_move):
            best_ms = ms
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]