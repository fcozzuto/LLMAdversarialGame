def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    self_terr = observation.get("self_territory", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    obstacles = observation.get("obstacles", []) or []

    self_set = set((int(x), int(y)) for x, y in self_terr)
    opp_set = set((int(x), int(y)) for x, y in opp_terr)
    un_set = set((int(x), int(y)) for x, y in unclaimed)
    obs_set = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_ours(x, y):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in self_set:
                c += 1
        return c

    def score_cell(x, y):
        if (x, y) in obs_set:
            return -10**9
        d_opp_now = abs(ox - sx) + abs(oy - sy)
        d_opp_next = abs(ox - x) + abs(oy - y)
        closer = d_opp_now - d_opp_next  # positive if moving toward opponent
        base = closer * 2

        if (x, y) in opp_set:
            base += 30  # flipping advantage
        elif (x, y) in self_set:
            base += 3 + 0.5 * adj_ours(x, y)
        elif (x, y) in un_set:
            base += 10 + 1.5 * adj_ours(x, y)  # expansion
        else:
            base += 4 + 0.5 * adj_ours(x, y)

        # Prefer staying/expanding toward boundary of our territory
        if (x, y) not in self_set:
            base += adj_ours(x, y) * 1.0
        return base

    # Deterministic tie-break: smaller dx, then smaller dy, then lexicographic by (x,y)
    best = (-10**18, 0, 0, sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        key = (sc, -abs(dx) - abs(dy), -nx, -ny)  # keeps deterministic preference
        if sc > best[0] or (sc == best[0] and key > (best[0], best[1], best[2], best[3], best[4])):
            best = (sc, dx, dy, nx, ny)

    return [int(best[1]), int(best[2])]