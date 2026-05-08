def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    self_cells = observation.get("self_territory") or []
    opp_cells = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    self_set = set((x, y) for x, y in self_cells)
    opp_set = set((x, y) for x, y in opp_cells)
    unclaimed_set = set((x, y) for x, y in unclaimed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    # candidate destination: prefer unclaimed cells that border our territory (expand) or opponent territory (pressure)
    behind = observation.get("self_territory_count", len(self_cells)) < observation.get("opponent_territory_count", len(opp_cells))
    best_dest = None
    best_key = None

    for ux, uy in unclaimed_set:
        adj_self = any((nx, ny) in self_set for nx, ny in neighbors8(ux, uy))
        adj_opp = any((nx, ny) in opp_set for nx, ny in neighbors8(ux, uy))
        if not (adj_self or adj_opp):
            continue
        dist = abs(ux - sx) + abs(uy - sy)
        # if behind, strongly prefer opponent-bordering to steal; else prefer our-bordering to secure
        score_bias = (0 if not behind else (-3 if adj_opp else 0)) + (2 if adj_self else 0)
        key = (dist, -int(adj_opp), -int(adj_self), score_bias, ux, uy)
        if best_key is None or key < best_key:
            best_key = key
            best_dest = (ux, uy)

    # if nothing suitable, fall back to nearest opponent cell (to flip if allowed), otherwise nearest unclaimed
    if best_dest is None:
        target_pool = opp_cells if behind and opp_cells else (unclaimed if unclaimed else [])
        if target_pool:
            tx, ty = min(target_pool, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
            best_dest = (tx, ty)
        else:
            best_dest = (sx, sy)

    tx, ty = best_dest
    # pick move that gets closest to target, breaking ties by avoiding obstacles
    best_move = (0, 0)
    best_dist = None
    best_tiebreak = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = abs(nx - tx) + abs(ny - ty)
            tieb = (-int((nx, ny) in opp_set), -int((nx, ny) in unclaimed_set), dx, dy, nx, ny)
            if best_dist is None or dist < best_dist or (dist == best_dist and tieb < best_tiebreak):
                best_dist = dist
                best_tiebreak = tieb
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]