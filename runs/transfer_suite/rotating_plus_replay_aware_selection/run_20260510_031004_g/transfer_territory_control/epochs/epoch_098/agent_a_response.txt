def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def center_score(x, y):
        d = abs(x - cx) + abs(y - cy)
        return -d

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        if (nx, ny) in self_terr:
            base = 0.5
        elif (nx, ny) in opp_terr:
            base = 5.5  # entering opponent cell flips control
        elif (nx, ny) in unclaimed:
            base = 4.0  # claim new territory
        else:
            base = 1.0  # safe fallback

        # Encourage attacking toward center and adjacent opportunities
        adj_bonus = 0.0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and not blocked(tx, ty):
                    if (tx, ty) in opp_terr:
                        adj_bonus += 0.6
                    elif (tx, ty) in unclaimed:
                        adj_bonus += 0.35

        sc = base + 0.9 * center_score(nx, ny) + adj_bonus
        key = (sc, -abs(dx), -abs(dy), dx, dy)
        if best_sc is None or key > best:
            best_sc = sc
            best = key
            best_move = [dx, dy]

    return best_move