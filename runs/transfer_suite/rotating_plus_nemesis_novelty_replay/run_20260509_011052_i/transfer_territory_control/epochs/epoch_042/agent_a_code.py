def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not self_terr:
        self_terr = {(sx, sy)}
    opp_list = list(opp_terr) if opp_terr else [(int(ox), int(oy))]

    def min_d_to_opp(x, y):
        bd = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < bd:
                bd = d
        return bd

    def adj_self_count(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self_terr:
                c += 1
        return c

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in opp_terr:
            sc += 7
        elif (nx, ny) in unclaimed:
            sc += 4
        elif (nx, ny) in self_terr:
            sc += 2

        sc += 1.2 * adj_self_count(nx, ny)
        sc += -0.08 * min_d_to_opp(nx, ny)  # prefer moving toward opponent when beneficial
        sc += 0.01 * (nx - sx) - 0.005 * (ny - sy)  # deterministic tie-break bias

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best