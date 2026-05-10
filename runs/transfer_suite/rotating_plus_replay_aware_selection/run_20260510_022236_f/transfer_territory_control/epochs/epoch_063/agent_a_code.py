def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    # Precompute opponent position for mild spacing
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    def adj_unclaimed_count(x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        d_from_opp = abs(x - ox) + abs(y - oy)
        boundary = adj_unclaimed_count(x, y)
        if (x, y) in self_terr:
            return 6 + 1.5 * boundary + 0.02 * d_from_opp
        if (x, y) in opp_terr:
            return 9 + 1.0 * boundary + 0.01 * d_from_opp
        if (x, y) in unclaimed:
            return 14 + 2.2 * boundary + 0.01 * d_from_opp
        return 2 + 0.6 * boundary + 0.02 * d_from_opp

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        # Deterministic tie-break: prefer non-stay, then smaller dx/dy lexicographically
        tie = (sc == best[0])
        if sc > best[0] or (tie and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]