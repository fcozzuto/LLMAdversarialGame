def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    opp_list = list(opp_terr) if opp_terr else [(int(ox), int(oy))]
    def dist_to_opp(x, y):
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best: best = d
        return best

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        val = 0.0
        if (nx, ny) in opp_terr:
            val += 55.0
        if (nx, ny) in self_terr:
            val += 8.0
        if (nx, ny) in unclaimed:
            val += 18.0

        adj_self = 0
        adj_opp = 0
        for ax, ay in dirs4:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in self_terr: adj_self += 1
            if (tx, ty) in opp_terr: adj_opp += 1
        val += 4.0 * adj_self
        val += 3.0 * adj_opp

        d = dist_to_opp(nx, ny)
        val += (16.0 / (1.0 + d))

        if dx == 0 and dy == 0:
            val -= 2.5

        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]