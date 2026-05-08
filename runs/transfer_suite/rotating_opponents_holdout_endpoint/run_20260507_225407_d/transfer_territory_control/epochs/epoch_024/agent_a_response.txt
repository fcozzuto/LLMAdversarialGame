def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    selfset = set((int(p[0]), int(p[1])) for p in self_terr if p and len(p) >= 2)
    opposet = set((int(p[0]), int(p[1])) for p in opp_terr if p and len(p) >= 2)
    unq = [(int(p[0]), int(p[1])) for p in unclaimed if p and len(p) >= 2]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If already adjacent to unclaimed frontier, go there to expand.
    frontier = []
    for (x, y) in unq:
        if (x, y) in selfset or (x, y) in opposet:
            continue
        adj_self = False
        adj_opp = False
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in selfset:
                adj_self = True
            if (nx, ny) in opposet:
                adj_opp = True
        frontier.append((x, y, 1 if adj_self else 0, 1 if adj_opp else 0))
    if frontier:
        # Score: prefer adj to self, then closer to us; otherwise prefer adj to opponent (faster contest).
        frontier.sort(key=lambda t: (-t[2], -t[3], abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - ox) + abs(t[1] - oy)))
        tx, ty = frontier[0][0], frontier[0][1]
    else:
        # No unclaimed: try to step into opponent territory (flipping) if possible, else move toward opponent.
        can_flip = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            if (nx, ny) in opposet:
                # Prefer closer to center of opponent territory.
                can_flip.append((abs(nx - ox) + abs(ny - oy), dx, dy))
        if can_flip:
            can_flip.sort(key=lambda t: (t[0], t[1], t[2]))
            return [can_flip[0][1], can_flip[0][2]]
        tx, ty = ox, oy

    # Choose move that reduces distance to target, avoiding obstacles; allow diagonal and staying.
    best = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # invalid move -> stay; deterministic penalty via distance
            nd = abs(nx - tx) + abs(ny - ty) + 1000
        else:
            nd = abs(nx - tx) + abs(ny - ty)
            # Small tie-break: prefer moving toward opponent if target not reachable well.
            nd += 0.01 * (abs(nx - ox) + abs(ny - oy))
        tup = (nd, dx, dy)
        if tup < best:
            best = tup
    return [int(best[1]), int(best[2])]