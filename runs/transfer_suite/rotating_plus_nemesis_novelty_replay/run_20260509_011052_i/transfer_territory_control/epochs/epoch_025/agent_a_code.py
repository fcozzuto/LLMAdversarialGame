def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    opp_anchor = (ox, oy) if not opp_terr else next(iter(opp_terr))
    def adj_self(x, y):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in self_terr:
                c += 1
        return c

    def adj_opp(x, y):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in opp_terr:
                c += 1
        return c

    def min_dist_to_opp(x, y):
        best = 10**9
        for px, py in (opp_terr if opp_terr else [opp_anchor]):
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        on_unclaimed = (nx, ny) in unclaimed
        on_self = (nx, ny) in self_terr
        on_opp = (nx, ny) in opp_terr
        if on_self:
            val = 0.5 * adj_self(nx, ny)
        elif on_unclaimed:
            val = 4.0 * adj_self(nx, ny) + 1.5 * (len(unclaimed) > 0) - 0.2 * adj_opp(nx, ny)
        elif on_opp:
            # Entering opponent territory flips control; attack only if it "connects" to our expansion
            val = 6.5 * adj_self(nx, ny) + 2.0 * adj_opp(nx, ny) - 0.3 * min_dist_to_opp(nx, ny)
        else:
            # stepping into unknown-but-open cells: prefer those near our territory and away from opponent
            val = 1.2 * adj_self(nx, ny) - 0.1 * min_dist_to_opp(nx, ny)

        # Stability: prefer not to step too close if it's not an actionable expansion/attack
        if not (on_unclaimed or on_opp):
            val -= 0.4 * min_dist_to_opp(nx, ny)

        # Deterministic tie-break: prefer smallest distance to opponent, then lexicographic move
        if val > best_val + 1e-9:
            best_val = val
            best_move = [dx, dy]
        elif abs(val - best_val) <= 1e-9:
            cand = (min_dist_to_opp(nx, ny), dx, dy)
            bestn = (min_dist_to_opp(sx + best_move[0], sy + best_move[1]), best_move[0], best_move[1])
            if cand < bestn:
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]