def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set(tuple(map(int, p)) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(map(int, p)) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(map(int, p)) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    if opp_terr:
        opp_list = list(opp_terr)
    else:
        opp_list = [(int(ox), int(oy))]

    def min_dist_to_opp(x, y):
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    def adj_self(x, y):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in self_terr:
                c += 1
        return c

    best = None
    best_val = -10**18
    # Head for cells that expand/control, especially if they can flip opponent territory.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0.0
        if (nx, ny) in opp_terr:
            val += 6.0  # flipping is valuable
        if (nx, ny) in unclaimed:
            val += 2.0  # claiming helps growth
        if (nx, ny) in self_terr:
            val += 0.5  # maintain/strengthen
        val += 0.9 * adj_self(nx, ny)  # prefer staying attached to our territory
        # Cut off opponent: prefer moving closer to their nearest cell while expanding
        val += -0.12 * min_dist_to_opp(nx, ny)
        # Slight bias to reduce corner-stalling: prefer moves that increase Chebyshev distance from own corner if possible
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        mycorner = min(corners, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        cur = max(abs(sx - mycorner[0]), abs(sy - mycorner[1]))
        nxt = max(abs(nx - mycorner[0]), abs(ny - mycorner[1]))
        val += 0.15 * (nxt - cur)
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]