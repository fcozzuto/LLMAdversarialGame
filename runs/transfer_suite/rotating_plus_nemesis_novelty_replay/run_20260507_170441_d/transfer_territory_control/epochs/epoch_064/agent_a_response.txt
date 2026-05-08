def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    nbrs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def eval_cell(x, y):
        if not inb(x, y) or (x, y) in blocked:
            return -10**9
        score = 0
        if (x, y) in opp_t:
            score += 60
        elif (x, y) in unclaimed:
            score += 28
        elif (x, y) in self_t:
            score += 8
        # Frontier pressure: move onto cells adjacent to opponent territory
        adj_opp = 0
        for dx, dy in nbrs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_t:
                adj_opp += 1
        score += adj_opp * 10
        # Avoid tight obstacle traps
        adj_obs = 0
        for dx, dy in nbrs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                adj_obs += 1
        score -= adj_obs * 2
        # Drift towards opponent side to keep a larger frontier
        dist_to_opp = abs(x - ox) + abs(y - oy)
        score -= dist_to_opp * 0.7
        return score

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
        v = eval_cell(nx, ny)
        if v > best_val:
            best_val = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]