def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    my_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    their_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obs = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    neigh_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def best_unclaimed_dist(x, y):
        # deterministic local "ray" preference: look for nearest unclaimed in small neighborhood
        best = 10**9
        for ddx in (-2, -1, 0, 1, 2):
            for ddy in (-2, -1, 0, 1, 2):
                nx, ny = x + ddx, y + ddy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    d = abs(nx - x) + abs(ny - y)
                    if d < best: best = d
        return best

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        val = 0
        if (nx, ny) in unclaimed: val += 140
        if (nx, ny) in their_terr: val += 160
        if (nx, ny) in my_terr: val += 15

        # expansion/connectivity to our territory
        conn = 0
        for ex, ey in neigh_dirs:
            tx, ty = nx + ex, ny + ey
            if (tx, ty) in my_terr: conn += 1
        val += 10 * conn

        # pressure: prefer moves that increase "distance from opponent" when on our frontier,
        # otherwise contest when close to them
        d_opp = abs(nx - ox) + abs(ny - oy)
        val += (6 if d_opp >= 6 else 0) - (8 if d_opp <= 2 else 0)

        # also prefer approaching nearby unclaimed (local) while not marching into opponent
        du = best_unclaimed_dist(nx, ny)
        if du < 10**9: val += 40 - 8 * du

        # slight bias toward reducing distance to opponent only if we can capture their territory/unclaimed near it
        if (nx, ny) in their_terr or du < 3:
            val += 0.5 * (10 - d_opp)

        if (val, -abs(nx - ox) - abs(ny - oy), -abs(nx - sx) - abs(ny - sy)) > (best[0], best[1], best[2]):
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]