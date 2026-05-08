def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    nbrs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj_opp = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def edge_pressure(x, y):
        c = 0
        for dx, dy in adj_opp:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) == (sx, sy):
            stay_pen = 0.3
        else:
            stay_pen = 0.0

        if (nx, ny) in opp_terr:
            base = 8.0
        elif (nx, ny) in unclaimed:
            base = 3.2
        elif (nx, ny) in self_terr:
            base = 1.0
        else:
            base = 1.2

        if (nx, ny) in resources:
            base += 2.0

        ep = edge_pressure(nx, ny)
        base += 0.9 * ep

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_self = abs(nx - (w // 2)) + abs(ny - (h // 2))
        base += 0.25 * (14 - d_opp)  # closer to opponent slightly better for edge trading
        base -= 0.15 * d_self

        # discourage giving opponent immediate capture pressure right next to them
        if max(abs(nx - ox), abs(ny - oy)) <= 1 and (nx, ny) not in self_terr:
            base -= 1.2

        base -= stay_pen

        # deterministic tie-break: prefer smallest (dx,dy) lexicographically
        key = (base, -ep, -d_opp, -d_self, dx, dy)
        if key[0] > best_sc:
            best_sc = key[0]
            best = [dx, dy]

    return best if best is not None else [0, 0]