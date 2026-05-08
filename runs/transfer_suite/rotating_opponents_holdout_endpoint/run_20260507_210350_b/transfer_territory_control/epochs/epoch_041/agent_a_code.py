def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    self_terr = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []))
    opp_terr = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []))
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mindist(x, y, S):
        if not S:
            return 10**9
        md = 10**9
        for (a, b) in S:
            d = abs(x - a) + abs(y - b)
            if d < md:
                md = d
        return md

    my_dist_to_opp = abs(sx - ox) + abs(sy - oy)
    opp_dist_to_me = my_dist_to_opp

    best = None
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in self_terr:
            sc += 6
        elif (nx, ny) in opp_terr:
            sc += 30
        elif (nx, ny) in unclaimed:
            sc += 12
        else:
            sc += 2

        # Boundary/adjacency pressure
        adj_opp = 0
        adj_self = 0
        adj_uncl = 0
        for ax, ay in neigh8:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty):
                continue
            if (tx, ty) in opp_terr:
                adj_opp += 1
            if (tx, ty) in self_terr:
                adj_self += 1
            if (tx, ty) in unclaimed:
                adj_uncl += 1
        sc += adj_opp * 4
        sc += adj_self * 2
        sc += adj_uncl * 1

        # Prefer moves that reduce distance to opponent when invading, otherwise expand locally
        nd_to_opp = abs(nx - ox) + abs(ny - oy)
        if (nx, ny) in opp_terr:
            sc += (my_dist_to_opp - nd_to_opp) * 3
        else:
            # keep pressure near the frontier: closer to opponent is slightly better
            sc += (opp_dist_to_me - nd_to_opp) * 1.2

        # Avoid getting stuck: small penalty for staying unless it improves local safety
        if dx == 0 and dy == 0:
            sc -= 1
            sc += adj_self * 1

        # Deterministic tie-break: fixed preference order by (sc, -nd_to_opp, dx, dy)
        key = (sc, -nd_to_opp, dx, dy)
        if key > (best_sc, -10**9, -2, -2):
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]