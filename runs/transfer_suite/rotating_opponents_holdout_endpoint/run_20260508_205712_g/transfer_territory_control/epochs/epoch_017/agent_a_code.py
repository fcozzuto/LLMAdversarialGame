def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles", []) or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))
    unC = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_type(x, y):
        if (x, y) in obstacles:
            return "obs"
        if (x, y) in selfT:
            return "self"
        if (x, y) in oppT:
            return "opp"
        if (x, y) in unC:
            return "un"
        return "other"

    def neigh_counts(x, y):
        uc = 0
        adj_opp = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) in unC:
                uc += 1
            if (nx, ny) in oppT:
                adj_opp += 1
        return uc, adj_opp

    if not selfT:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        t = cell_type(nx, ny)
        base = 0
        if t == "self":
            base = 0.2
        elif t == "un":
            base = 2.0
        elif t == "opp":
            base = 3.5
        else:
            base = 0.7 if (nx, ny) in unC else 0.0
        uc, adj_opp = neigh_counts(nx, ny)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        # Prefer expansion and pressure; slight preference for moving away when not attacking.
        attack = 0.8 * adj_opp + 0.15 * uc
        spread = 0.05 * (w + h - dist_opp)
        guard = -0.02 * (1 if t == "self" else 0) * dist_opp
        score = base + 0.9 * uc + attack + spread + guard
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move