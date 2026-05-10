def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_territory = observation.get("self_territory", []) or []
    opp_territory = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    obstacles = observation.get("obstacles", []) or []
    oxp, oyp = observation.get("opponent_position", (w - 1, h - 1))

    self_set = set((int(p[0]), int(p[1])) for p in self_territory)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_territory)
    unclaimed_set = set((int(p[0]), int(p[1])) for p in unclaimed)
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    if opp_set:
        ax = sum(x for x, y in opp_set) / len(opp_set)
        ay = sum(y for x, y in opp_set) / len(opp_set)
        opp_cx, opp_cy = int(ax), int(ay)
    else:
        opp_cx, opp_cy = int(oxp), int(oyp)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in S:
                c += 1
        return c

    def dist_to_opp_center(x, y):
        return abs(opp_cx - x) + abs(opp_cy - y)

    best_dxdy = [0, 0]
    best = -10**18

    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) in self_set:
            base = -0.2 * dist_to_opp_center(nx, ny) + 0.1 * adj_count(nx, ny, self_set)
        elif (nx, ny) in unclaimed_set:
            base = 5.0 + 1.2 * adj_count(nx, ny, self_set) - 0.1 * dist_to_opp_center(nx, ny)
        elif (nx, ny) in opp_set:
            base = 9.0 + 1.8 * adj_count(nx, ny, self_set) - 1.0 * adj_count(nx, ny, opp_set) - 0.05 * dist_to_opp_center(nx, ny)
        else:
            base = -0.5 + 0.2 * adj_count(nx, ny, self_set)

        if (nx, ny) != (sx, sy):
            base += 0.3 * (dist_to_opp_center(sx, sy) - dist_to_opp_center(nx, ny))
        base += 0.05 * (adj_count(nx, ny, self_set) - adj_count(nx, ny, opp_set))

        if base > best:
            best = base
            best_dxdy = [int(dx), int(dy)]

    return best_dxdy