def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                rlist.append((rx, ry))

    if not rlist:
        best = (None, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # Prefer staying away from opponent when no resources exist
            key = (abs(nx - ox) + abs(ny - oy), -abs(dx) - abs(dy), -dx - dy)
            if best[0] is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best[0] is not None else [0, 0]

    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        our_min = 10**9
        opp_min = 10**9
        our_best = 10**9
        opp_best = 10**9
        for rx, ry in rlist:
            d1 = abs(nx - rx) + abs(ny - ry)
            if d1 < our_min:
                our_min = d1
                our_best = d1
            d2 = abs(ox - rx) + abs(oy - ry)
            if d2 < opp_min:
                opp_min = d2
                opp_best = d2

        # Lead: how much closer we are than opponent to the nearest resource
        # Small tie-break: avoid moving closer to opponent unless it also improves lead
        lead = (opp_min - our_min)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        key = (lead, dist_opp, -our_min, -(dx * dx + dy * dy), -dx, -dy)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]