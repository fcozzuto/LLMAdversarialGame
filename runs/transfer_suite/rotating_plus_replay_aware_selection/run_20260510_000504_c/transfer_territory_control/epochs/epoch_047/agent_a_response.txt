def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_cells(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            xx, yy = x + dx, y + dy
            if inb(xx, yy):
                yield xx, yy

    # Build a deterministic "frontier" target: unclaimed cells adjacent to opponent territory,
    # else unclaimed anywhere, else resources, else opponent territory, else self.
    frontier = []
    for (ox, oy) in opp_terr:
        for xx, yy in adj_cells(ox, oy):
            if (xx, yy) in unclaimed:
                frontier.append((xx, yy))
    if not frontier and unclaimed:
        frontier = list(unclaimed)
    if not frontier and resources:
        frontier = list(resources)
    if not frontier:
        frontier = list(opp_terr) if opp_terr else list(self_terr) if self_terr else [(sx, sy)]

    tx, ty = min(frontier, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))

    best_move = (0, 0)
    best_score = -10**9

    def cell_reward(x, y):
        if (x, y) in obstacles:
            return -10**9
        r = 0
        if (x, y) in unclaimed:
            r += 6
        if (x, y) in opp_terr:
            r += 7  # likely flip
        if (x, y) in self_terr:
            r += 2
        if (x, y) == (sx, sy):
            r += 0  # staying has no direct value
        # Encourage progress and local expansion
        d = abs(x - tx) + abs(y - ty)
        r += 3 - d  # prefer smaller distance
        # Edge leverage: adjacency to unclaimed/opp territory
        a = 0
        for xx, yy in adj_cells(x, y):
            if (xx, yy) in unclaimed:
                a += 2
            if (xx, yy) in opp_terr:
                a += 1
        r += a
        return r

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        sc = cell_reward(nx, ny)
        # Deterministic tie-break: higher score, then smaller (dx,dy) lexicographically.
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]