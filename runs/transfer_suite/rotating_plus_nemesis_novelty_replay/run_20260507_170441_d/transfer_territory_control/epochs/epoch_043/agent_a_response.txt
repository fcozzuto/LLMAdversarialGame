def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny, dx, dy = sx, sy, 0, 0

        v = 0
        if (nx, ny) in opp_t:
            v += 260  # allow counterclaim flip when it yields territory immediately
        elif (nx, ny) in unclaimed:
            v += 520
        elif (nx, ny) in self_t:
            v -= 40  # avoid wasting turns

        # pressure: unclaimed adjacent to opponent territory
        adj_opp = 0
        adj_self = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if not inb(px, py):
                    continue
                if (px, py) in opp_t:
                    adj_opp += 1
                if (px, py) in self_t:
                    adj_self += 1
        v += 70 * adj_opp
        v += 10 * adj_self

        # centralization and opponent proximity control
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v += 35 - 6 * (abs(nx - cx) + abs(ny - cy))  # prefer center growth
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        v += 18 - 3 * d_to_opp  # stay near to contest

        # anti-stagnation: discourage exact repeats by favoring moves that change position
        if dx == 0 and dy == 0:
            v -= 25

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best