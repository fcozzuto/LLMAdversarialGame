def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    my_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    their_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        val = 0
        if (nx, ny) in unclaimed:
            val += 80
        if (nx, ny) in their_terr:
            val += 120
        # Prefer moves that connect to our territory and create pressure near opponent territory.
        neigh = 0
        near_their = 0
        near_unclaimed = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if not inb(ax, ay):
                    continue
                if (ax, ay) in my_terr:
                    neigh += 1
                if (ax, ay) in their_terr:
                    near_their += 1
                if (ax, ay) in unclaimed:
                    near_unclaimed += 1
        val += 8 * neigh + 12 * near_their + 3 * near_unclaimed
        # Mild goal: drift toward opponent to keep tempo.
        val -= (abs(nx - ox) + abs(ny - oy)) * 0.5
        # Extra: avoid stepping away from our frontier if we're currently small.
        val -= (abs(nx - sx) + abs(ny - sy)) * 0.05
        if val > best[0] or (val == best[0] and (dx, dy) < (best[1], best[2])):
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]