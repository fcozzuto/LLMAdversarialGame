def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs8 = moves

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neigh_count(cell, target_set):
        x, y = cell
        c = 0
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in target_set:
                c += 1
        return c

    # Build a cheap deterministic "frontier" set: unclaimed cells adjacent to opponent territory.
    frontier = set()
    for (x, y) in opp_terr:
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                frontier.add((nx, ny))

    best = None
    bestv = -1e18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        cell = (nx, ny)
        base = 0.0
        if cell in opp_terr:
            base += 8.0
        elif cell in unclaimed:
            base += 3.5
        elif cell in self_terr:
            base += 1.0
        else:
            base += 0.5

        if cell in resources:
            base += 2.0

        # Drive toward frontier if it exists; otherwise toward unclaimed generally.
        target_set = frontier if frontier else unclaimed
        if target_set:
            d = min(dist(cell, t) for t in target_set)
            base += 2.2 / (1 + d)

        # Prefer states that increase contact with opponent territory (encourages counterclaim pressure).
        base += 0.65 * neigh_count(cell, opp_terr)

        # Slightly avoid walking into opponent proximity without sacrificing immediate claim gain.
        d_to_opp = dist(cell, (ox, oy))
        base += 0.15 * d_to_opp

        # Tie-break deterministically by favoring moves that keep x closer to increasing direction toward center
        # and then lower dx,dy order.
        tie = (base, -abs(nx - (w // 2)), -abs(ny - (h // 2)), -abs(dx), -abs(dy), dx, dy)

        if tie[0] > bestv:
            bestv = tie[0]
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best