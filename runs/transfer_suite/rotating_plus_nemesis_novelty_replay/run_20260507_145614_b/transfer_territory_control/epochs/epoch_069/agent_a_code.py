def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))
    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def neigh8(x, y):
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny
    opp_adj = set()
    for x, y in opp_set:
        for nx, ny in neigh8(x, y):
            if (nx, ny) not in opp_set:
                opp_adj.add((nx, ny))
    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = 0
        sc += 5000 if (nx, ny) in opp_adj else 0
        sc += 2000 if (nx, ny) in opp_set else 0
        sc += 5 * (1 if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1) else 0)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        sc += -dist_opp
        if unclaimed:
            md = None
            for x, y in unclaimed:
                if (x, y) in opp_set:
                    continue
                d = abs(nx - x) + abs(ny - y)
                if md is None or d < md:
                    md = d
            if md is not None:
                sc += -2 * md
        if best is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]