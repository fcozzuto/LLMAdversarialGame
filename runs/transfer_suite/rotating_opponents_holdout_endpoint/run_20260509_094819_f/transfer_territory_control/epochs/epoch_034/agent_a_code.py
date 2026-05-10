def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    myc = int(observation.get("self_territory_count", len(selfT)))
    oppc = int(observation.get("opponent_territory_count", len(oppT)))
    behind = 1 if myc < oppc else 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    def nearest_d2(x, y, S):
        if not S:
            return 10**9
        best = 10**9
        for (a, b) in S:
            v = d2(x, y, a, b)
            if v < best:
                best = v
        return best

    # Decide preference: when behind, hunt opponent; when ahead, expand unclaimed.
    prefer_opp = behind
    prefer_uncl = 1 - behind

    # Precompute distances from current position for tie-breaking robustness.
    nd2_uncl_now = nearest_d2(sx, sy, unclaimed)
    nd2_opp_now = nearest_d2(sx, sy, oppT)

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**12
        if not inb(x, y):
            return -10**12
        if (x, y) in selfT:
            base = 5
        elif (x, y) in oppT:
            base = 22 if prefer_opp else 10
        elif (x, y) in unclaimed:
            base = 20 if prefer_uncl else 9
        else:
            base = 3

        # Encourage progress: move closer to chosen target set.
        if prefer_uncl:
            nd = nearest_d2(x, y, unclaimed)
            prog = (nd2_uncl_now - nd)
            base += 2.0 * prog
        else:
            nd = nearest_d2(x, y, oppT)
            prog = (nd2_opp_now - nd)
            base += 2.0 * prog

        # Slightly prefer moves that expand frontier around the chosen territory.
        neigh = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
        c = 0
        if prefer_uncl:
            for nx, ny in neigh:
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    c += 1
        else:
            for nx, ny in neigh:
                if inb(nx, ny) and (nx, ny) in oppT:
                    c += 1
        base += 0.6 * c

        # Discourage oscillation: if we move into a cell we already own, keep smaller than into new claims.
        return base

    # Deterministic tie-breaking: max score, then lexicographic dx,dy preference order.
    best = -10**18
    best_move = (0, 0)
    order = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (0, -1): 3, (-1, 0): 4, (1, 1): 5, (-1, 1): 6, (1, -1): 7, (-1, -1): 8}
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best or (sc == best and order[(dx, dy)] < order[best_move]):
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]