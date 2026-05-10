def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp_t = observation.get("opponent_territory", []) or []
    opp = set((p[0], p[1]) for p in opp_t)
    unclaimed = observation.get("unclaimed_cells", []) or []
    un = set((p[0], p[1]) for p in unclaimed)
    self_t = observation.get("self_territory", []) or []
    selfs = set((p[0], p[1]) for p in self_t)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h

    def score_cell(cx, cy):
        # Prefer unclaimed frontier; penalize opponent adjacency; avoid being stuck near enemy.
        if (cx, cy) in obs: return -10**9
        if (cx, cy) in opp: return -50 - (abs(cx - x) + abs(cy - y))
        if (cx, cy) in un:
            frontier = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: continue
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) in selfs: frontier = 1
            val = 40 if frontier else 10
        else:
            # Our territory is safe but expand incrementally
            val = 5 if (cx, cy) in selfs else 0
        # Opponent pressure: distance to nearest opponent territory cell
        md = 10**9
        for (ox, oy) in opp_t:
            d = abs(ox - cx) + abs(oy - cy)
            if d < md: md = d
        if md < 10:
            val -= (10 - md) * 3
        # Encourage moving outward from the center slightly (keeps map control)
        cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(cx - cx0) + abs(cy - cy0)
        val += dist_center * 0.02
        # Small tie-breaker toward current position stability
        val -= (abs(cx - x) + abs(cy - y)) * 0.01
        return val

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = score_cell(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]