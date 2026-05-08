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
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def sgn(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in self_terr:
            base = 2
        elif (x, y) in unclaimed:
            base = 8
        elif (x, y) in opp_terr:
            base = 7  # flipping gives value; prefer contesting over dead ends
        else:
            base = 4
        # Prefer moving toward center and expanding boundary (toward unclaimed)
        distc = abs(x - cx) + abs(y - cy)
        base += (14 - distc) * 0.15
        # Local frontier bonus
        nb_un = 0
        for ax, ay in dirs:
            nx, ny = x + ax, y + ay
            if inb(nx, ny) and (nx, ny) in unclaimed:
                nb_un += 1
        # Mild avoidance of stepping into pockets (surrounded by obstacles/enemy)
        nb_block = 0
        for ax, ay in dirs:
            nx, ny = x + ax, y + ay
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nb_block += 1
        base += nb_un * 2.2 - nb_block * 0.25
        return base

    # Deterministic tie-break order: iterate dirs in fixed order; compute best by value, then closer to center, then lexicographic move
    best_move = [0, 0]
    best_val = -10**18
    best_dcenter = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = cell_value(nx, ny)
        dcenter = abs(nx - cx) + abs(ny - cy)
        if val > best_val or (val == best_val and (dcenter < best_dcenter or (dcenter == best_dcenter and (dx, dy) < tuple(best_move)))):
            best_val = val
            best_dcenter = dcenter
            best_move = [dx, dy]

    # If stuck (all moves blocked), attempt staying; otherwise return best.
    return best_move