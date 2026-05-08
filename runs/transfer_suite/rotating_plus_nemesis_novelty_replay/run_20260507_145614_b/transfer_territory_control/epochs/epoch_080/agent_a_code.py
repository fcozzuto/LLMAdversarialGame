def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((p[0], p[1]) for p in self_terr if p and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles)
    opp_set = set((p[0], p[1]) for p in opp_terr if p and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles)

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((p[0], p[1]) for p in unclaimed if p and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obstacles)

    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    oppx, oppy = opp_pos[0], opp_pos[1]
    if opp_set:
        ax = ay = 0
        for (x, y) in opp_set:
            ax += x
            ay += y
        oppx = ax // len(opp_set)
        oppy = ay // len(opp_set)

    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def n8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    yield nx, ny

    opts = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        flip = 1 if (nx, ny) in opp_set else 0
        edge = (1 if nx in (0, w - 1) else 0) + (1 if ny in (0, h - 1) else 0)
        dist_opp = abs(nx - oppx) + abs(ny - oppy)
        adj_un = sum((a, b) in un_set for (a, b) in n8(nx, ny))
        adj_opp = sum((a, b) in opp_set for (a, b) in n8(nx, ny))
        adj_self = sum((a, b) in self_set for (a, b) in n8(nx, ny))
        # Prefer flipping opponent territory immediately; otherwise push outward and grow toward unclaimed.
        val = (flip * 1000) + (adj_opp * 30) + (adj_self * 8) + (adj_un * 6) + (dist_opp * 3) + (edge * 5)
        key = (val, dist_opp, edge, adj_un, -dx, -dy)  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]