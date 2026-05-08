def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((p[0], p[1]) for p in self_terr if p and len(p) >= 2)
    opp_set = set((p[0], p[1]) for p in opp_terr if p and len(p) >= 2)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    # Frontier targeting: prefer unclaimed cells that are adjacent to opponent territory (edge claim).
    # Fall back to unclaimed, else toward the closest unclaimed/opp territory cell.
    opp_adj = []
    for (x, y) in unclaimed:
        if any((nx, ny) in opp_set for (nx, ny) in neighbors8(x, y)):
            opp_adj.append((x, y))

    candidates = opp_adj if opp_adj else unclaimed

    if candidates:
        best = None
        best_k = None
        for x, y in candidates:
            if (x, y) in self_set:
                continue
            d_me = man(sx, sy, x, y)
            d_opp = man(ox, oy, x, y)
            # Prefer quick captures, being "closer" than opponent, and directly adjacent to opponent.
            adj_score = 1 if any((nx, ny) in opp_set for (nx, ny) in neighbors8(x, y)) else 0
            k = (d_me, -d_opp, -adj_score, x, y)
            if best_k is None or k < best_k:
                best_k = k
                best = (x, y)
        tx, ty = best
    else:
        # No unclaimed info: chase a point on/near opponent territory.
        if opp_terr:
            tx, ty = min(opp_terr, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
        else:
            # Last resort: move toward center.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            tx, ty = cx, cy

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]