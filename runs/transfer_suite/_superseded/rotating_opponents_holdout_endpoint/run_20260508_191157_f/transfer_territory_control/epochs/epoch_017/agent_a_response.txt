def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        moves.append((nx, ny, dx, dy))
    if not moves:
        return [0, 0]

    opp_adj = set()
    for (x, y) in opp_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inside(nx, ny):
                    opp_adj.add((nx, ny))

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in opp_terr:
            base = 3000
        else:
            base = 0
        if (x, y) in unclaimed:
            base += 200
        if (x, y) in self_terr:
            base -= 5
        # Encourage boundary fighting and closing toward opponent
        adj_opp = 0
        adj_self = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not inside(nx, ny):
                    continue
                if (nx, ny) in opp_terr:
                    adj_opp += 1
                if (nx, ny) in self_terr:
                    adj_self += 1
        base += adj_opp * 60 + adj_self * 10
        # Prefer reducing distance to opponent when attacking, otherwise slightly prefer edges
        man_op = abs(x - ox) + abs(y - oy)
        base += (-man_op) * (3 if (x, y) in opp_adj or (x, y) in unclaimed else 1)
        if x in (0, w - 1) or y in (0, h - 1):
            base += 12
        return base

    best = None
    best_key = None
    for x, y, dx, dy in moves:
        val = score_cell(x, y)
        # deterministic tie-break: prefer lower dx, then lower dy, then lexicographic position
        key = (val, -abs(x - ox) - abs(y - oy), dx, dy, x, y)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]