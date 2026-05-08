def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))

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
    unclaimed = [(int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or [])]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_has_opp_adj(c):
        cx, cy = c
        for dx, dy in neigh8:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in opp_t:
                return True
        return False

    # Choose target unclaimed cell: prioritize cells adjacent to opponent, then closeness to our front.
    target = None
    if unclaimed:
        if opp_t:
            candidates = [c for c in unclaimed if cell_has_opp_adj(c)]
            cand_list = candidates if candidates else unclaimed
        else:
            cand_list = unclaimed

        # Distance to nearest of our territory (or our position if we have none)
        base_set = self_t if self_t else {(sx, sy)}
        for c in cand_list:
            d_self = min(dist(c, p) for p in base_set)
            d_opp = min(dist(c, p) for p in opp_t) if opp_t else 0
            # Prefer grabbing near opponent, but not too far from our body
            score = (0 if cell_has_opp_adj(c) else 50) + 2 * d_self - 1 * d_opp
            if target is None or score < target[0]:
                target = (score, c)
    tx, ty = target[1] if target else (ox, oy)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
        # Heuristic: minimize distance to target; tie-breaker: slightly prefer moving away from opponent if target absent.
        d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(nx - ox) + abs(ny - oy)
        val = (d, -opp_d if target is None else opp_d)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]