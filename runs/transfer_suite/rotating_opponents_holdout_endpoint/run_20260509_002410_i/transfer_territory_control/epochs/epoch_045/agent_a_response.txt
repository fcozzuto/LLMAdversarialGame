def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_opp_dist(cell):
        if not opp_t:
            return 99
        return min(man(cell, p) for p in opp_t)

    def adj_cnt(cell, sset):
        x, y = cell
        c = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            if (x + dx, y + dy) in sset:
                c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_list = list(opp_t)
    best = None
    best_m = (0, 0)

    # Deterministic tie-break: fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        n = (nx, ny)

        if n in opp_t:
            # Capturing opponent territory is valuable; prioritize closer targets
            val = 420 - 3 * nearest_opp_dist(n) + 2 * adj_cnt(n, self_t) - 2 * adj_cnt(n, opp_t)
        elif n in unclaimed:
            # Expand into unclaimed, especially near opponent and supported by our territory
            val = 180 + 6 * adj_cnt(n, opp_t) + 4 * adj_cnt(n, self_t) - 1 * nearest_opp_dist(n)
            # Edge pressure a bit
            if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
                val += 20
        elif n in self_t:
            # Stay on our territory but advance toward open/contested cells
            val = 70 + 3 * adj_cnt(n, unclaimed) + 2 * adj_cnt(n, opp_t) - 1 * nearest_opp_dist(n)
        else:
            val = 5  # should be rare

        # Mild tendency to move toward the closest unclaimed edge/frontier
        if unclaimed:
            edge_un = [c for c in unclaimed if c[0] in (0, w - 1) or c[1] in (0, h - 1)]
            focus = edge_un if edge_un else list(unclaimed)
            t = focus[0]
            bd = 10**9
            for c in focus[:32]:  # deterministic slice
                d = man(n, c)
                if d < bd:
                    bd = d
                    t = c
            val += 12 - min(12, bd)

        if best is None or val > best:
            best = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]