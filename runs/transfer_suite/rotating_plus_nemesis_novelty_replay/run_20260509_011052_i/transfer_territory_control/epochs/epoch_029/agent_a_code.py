def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_list = list(opp_terr) if opp_terr else [(int(ox), int(oy))]

    def manh(x, y, px, py):
        return abs(px - x) + abs(py - y)

    def min_dist_to_opp(x, y):
        d = 10**9
        for px, py in opp_list:
            t = manh(x, y, px, py)
            if t < d:
                d = t
        return d

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        if not inb(x, y):
            return -10**9
        base = 0
        if (x, y) in self_terr:
            base += 2
        if (x, y) in unclaimed:
            base += 6
        if (x, y) in opp_terr:
            base += 10  # flip on entry
        # Encourage moving toward valuable fronts without overcommitting
        d = min_dist_to_opp(x, y)
        base += max(0, 4 - d)  # closer to opponent territory is better
        # Avoid getting stuck: prefer cells adjacent to unclaimed or our own territory
        adj = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and ((nx, ny) in unclaimed or (nx, ny) in self_terr or (nx, ny) in opp_terr):
                adj += 1
        base += adj * 0.7
        # Slightly prefer reducing distance to opponent position
        base += 0.1 * (-(manh(x, y, ox, oy)))
        return base

    best = [0, 0]
    best_sc = -10**18
    # Deterministic tie-break: fixed dir order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best