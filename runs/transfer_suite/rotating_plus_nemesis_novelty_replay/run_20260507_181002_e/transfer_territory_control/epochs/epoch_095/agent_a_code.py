def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    # Prefer contesting unclaimed near opponent; counterclaim if ahead, expand if behind
    self_count = int(observation.get("self_territory_count", len(selfT)))
    opp_count = int(observation.get("opponent_territory_count", len(oppT)))
    ahead = self_count > opp_count

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in selfT:
            base = 0.5
        else:
            base = 0.0
        if (x, y) in unclaimed:
            base += 3.0
        if (x, y) in oppT:
            base += 6.0 if not ahead else 7.0  # be extra aggressive when ahead
        # Path pressure: move toward opponent frontier, but avoid giving up distance when losing
        d_to_opp = abs(x - ox) + abs(y - oy)
        d_now = abs(sx - ox) + abs(sy - oy)
        # If losing, close distance; if ahead, maintain pressure but don't chase blindly
        if ahead:
            base += 0.15 * (d_now - d_to_opp)  # slight push toward opponent
        else:
            base += 0.35 * (d_now - d_to_opp)  # stronger push toward opponent
        # Soft preference for edges when safe (avoid central stalemates)
        edge_bonus = 0.05 * (x == 0 or x == w - 1 or y == 0 or y == h - 1)
        return base + edge_bonus

    best = (-(10**18), None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        val = score_cell(nx, ny)
        if val > best[0]:
            best = (val, (dx, dy))
    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]