def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (w - 1, h - 1)))
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2}
    resources = {(int(p[0]), int(p[1])) for p in (observation.get("resources") or []) if p and len(p) >= 2}
    unclaimed = {(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2}
    self_terr = {(int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2}
    opp_terr = {(int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cell_value(x, y):
        if not inside(x, y) or (x, y) in obstacles: return -10**9
        base = 0.0
        if (x, y) in opp_terr: base += 7.5
        elif (x, y) in unclaimed: base += 3.0
        elif (x, y) in self_terr: base += 1.0
        else: base += 0.2
        if (x, y) in resources: base += 4.0
        # Frontier bonus: reward stepping near opponent territory or unclaimed.
        n = [(x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y-1),(x-1,y+1),(x+1,y+1)]
        near_opp = sum(1 for (a,b) in n if inside(a,b) and (a,b) in opp_terr)
        near_un = sum(1 for (a,b) in n if inside(a,b) and (a,b) in unclaimed)
        base += 1.2 * near_opp + 0.6 * near_un
        # Competitive pressure: prefer reducing distance to opponent when contesting.
        dist_opp = abs(x - ox) + abs(y - oy)
        base += 0.25 * (14 - dist_opp)
        # Safety: if opponent is adjacent and we would move into their territory, ensure we don't get trapped by obstacles (light).
        if (x, y) in opp_terr and dist_opp <= 2:
            free_neighbors = 0
            for (a,b) in n[:4]:
                if inside(a,b) and (a,b) not in obstacles: free_neighbors += 1
            base += 0.3 * free_neighbors
        return base

    best = None
    best_sc = -10**18
    # Deterministic tie-break by move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = cell_value(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]