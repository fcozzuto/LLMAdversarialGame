def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_pen(x, y):
        d = min(x, y, w - 1 - x, h - 1 - y)
        return (4 - d)  # more penalty near edges

    def neigh_count(cell, terrset):
        x, y = cell
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in terrset:
                c += 1
        return c

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_pos = observation.get("opponent_position", (w - 1, h - 1))
    opp_pos = (int(opp_pos[0]), int(opp_pos[1]))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0.0
        if (x, y) in unclaimed:
            s += 6.0
            s += 0.6 * neigh_count((x, y), self_terr)
            s -= 1.2 * neigh_count((x, y), opp_terr)
        elif (x, y) in opp_terr:
            s += 2.0
            s -= 2.0 * neigh_count((x, y), opp_terr)
            s -= 0.7 * (manh((x, y), opp_pos) == 0)
        elif (x, y) in self_terr:
            s += 1.5
        else:
            s += 0.8
        s -= 0.9 * edge_pen(x, y)
        s += 0.25 * (-manh((x, y), opp_pos))  # keep away from opponent
        s += -0.05 * ((x - cx) ** 2 + (y - cy) ** 2)  # prefer center
        return s

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # 2-step lookahead to break ties deterministically
        sc1 = score_cell(nx, ny)
        best2 = -10**18
        for ddx, ddy in dirs:
            nnx, nny = nx + ddx, ny + ddy
            if not inb(nnx, nny) or (nnx, nny) in obstacles:
                continue
            best2 = max(best2, score_cell(nnx, nny))
        total = sc1 + 0.35 * (best2 if best2 > -10**17 else 0.0)
        # deterministic tie-break: prefer larger dx then larger dy then closer to center
        if total > best[0] or (total == best[0] and (dx, dy, -((nx-cx)**2+(ny-cy)**2)) > (best[1], best[2], best[3] if len(best) > 3 else 0)):
            best = (total, dx, dy, -((nx - cx) ** 2 + (ny - cy) ** 2))
    return [int(best[1]), int(best[2])]