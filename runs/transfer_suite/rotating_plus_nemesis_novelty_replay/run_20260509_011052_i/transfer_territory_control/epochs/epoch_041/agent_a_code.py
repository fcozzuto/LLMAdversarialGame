def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    opp_list = list(opp_terr) if opp_terr else [(int(ox), int(oy))]
    def min_dist_to_opp(x, y):
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    base_d = min_dist_to_opp(sx, sy)
    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 3
        if (nx, ny) in self_terr:
            sc += 1
        if (nx, ny) in opp_terr:
            sc += 7
        sc += 2 * adj_count(nx, ny, self_terr)
        sc += 1 * adj_count(nx, ny, unclaimed)
        d = min_dist_to_opp(nx, ny)
        sc += 2 * (base_d - d)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best