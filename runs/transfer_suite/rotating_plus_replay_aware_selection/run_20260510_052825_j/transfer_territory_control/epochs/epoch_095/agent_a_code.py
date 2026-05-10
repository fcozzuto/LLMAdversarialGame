def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (sx, sy) in obstacles:
        dirs = [(0, 0)]

    def score_cell(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9

        val = 0.0
        if (nx, ny) in unclaimed:
            val += 12.0
        if (nx, ny) in oppT:
            val += 7.0
        if (nx, ny) in selfT:
            val += 2.0

        # Prefer expanding from frontier: cells adjacent to our territory
        frontier_adj = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in selfT:
                frontier_adj += 1
        val += 1.5 * frontier_adj

        # Slightly prefer moves that keep distance from opponent while contesting space
        if isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2:
            px, py = opp_pos
            d = abs(nx - px) + abs(ny - py)
            val += 0.05 * d  # stay away (territory counterclaim)
            # If adjacent to opponent territory, reduce distance penalty (counterclaim)
            if (nx, ny) in oppT:
                val += 1.0

        # Avoid getting stuck inside fully-owned region: prefer cells with fewer self-neighbors
        self_neighbors = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in selfT:
                self_neighbors += 1
        val += -0.15 * self_neighbors

        return val

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        if v > best_val + 1e-9:
            best_val = v
            best = (dx, dy)
        elif abs(v - best_val) <= 1e-9:
            if best is None or (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]