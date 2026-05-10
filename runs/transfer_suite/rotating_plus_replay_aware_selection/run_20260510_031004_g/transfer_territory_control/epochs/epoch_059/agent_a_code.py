def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", [])))
    self_pos = (sx, sy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    neigh8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def any_neigh(cell, terr):
        x, y = cell
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in terr:
                return True
        return False

    # Prefer unclaimed frontier cells next to our territory; then fall back to any unclaimed;
    # if none, go toward opponent territory to counter-claim.
    frontier = []
    for c in unclaimed:
        if any_neigh(c, self_terr):
            frontier.append(c)
    candidates = frontier if frontier else (unclaimed if unclaimed else list(opp_terr))
    if not candidates:
        return [0, 0]

    # Deterministic target selection: closest, and slightly prefer cells adjacent to opponent.
    best = None
    for c in candidates:
        d = dist(self_pos, c)
        adj_opp = 1 if any_neigh(c, opp_terr) else 0
        # tie-breakers: fewer steps overall, then lexicographic
        key = (d, -adj_opp, c[0], c[1])
        if best is None or key < best[0]:
            best = (key, c)
    tx, ty = best[1]

    # Choose best immediate move (among 9 deltas), avoiding obstacles.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break order: prioritize moves that reduce distance; then lexicographic by delta.
    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d2 = dist((nx, ny), (tx, ty))
        # Small preference to not stand still if equally good.
        key = (d2, 1 if (dx == 0 and dy == 0) else 0, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move