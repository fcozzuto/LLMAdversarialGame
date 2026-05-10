def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    self_ter = set(map(tuple, observation.get("self_territory", []) or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # If stuck (all neighbors invalid), allow staying.
    if not dirs:
        return [0, 0]

    def mindist_to_set(x, y, S, default=99):
        best = default
        for (tx, ty) in S:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    # Select targets from unclaimed; bias toward edges to pressure.
    edge_unclaimed = [(x, y) for (x, y) in unclaimed if x in (0, w - 1) or y in (0, h - 1)]
    targets = edge_unclaimed if edge_unclaimed else list(unclaimed)
    # Keep targets small/deterministic.
    if len(targets) > 12:
        # choose closest 4 to self, then closest to opponent if tie-like
        ox, oy = observation.get("opponent_position", (w - 1, h - 1))
        targets.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - ox) + abs(p[1] - oy), p[0], p[1]))
        targets = targets[:12]

    opp_points = list(opp_ter)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Ownership-based scoring (prefer capturing opponent territory when adjacent)
        if (nx, ny) in opp_ter:
            val = 1000.0
        elif (nx, ny) in self_ter:
            val = -50.0  # avoid wasting moves inside own area when spreading matters
        elif (nx, ny) in unclaimed:
            val = 220.0
        else:
            val = 80.0  # neutral/unknown

        # Prefer moves that get closer to unclaimed targets
        if targets:
            d_un = min(abs(tx - nx) + abs(ty - ny) for (tx, ty) in targets)
            val += 15.0 * (-d_un)
        else:
            # Otherwise, push toward center
            val += -5.0 * (abs(nx - center_x) + abs(ny - center_y))

        # Prefer reducing distance to opponent territory "front"
        if opp_points:
            d_opp = min(abs(px - nx) + abs(py - ny) for (px, py) in opp_points)
            val += 8.0 * (-d_opp)

        # Slight bias to avoid moving directly away from opponent (keeps pressure)
        dist_from_opp = abs(nx - ox) + abs(ny - oy)
        val += -0.5 * dist_from_opp

        # Deterministic tie-breaker: smallest dx, then smallest dy toward a fixed preference order
        if val > best_val + 1e-9:
            best_val = val
            best_move = (dx, dy)
        elif abs(val - best_val) <= 1e-9:
            # prefer moves with dx,dy closer to (1,1) then (0,0)
            pref = (abs(dx - 1) + abs(dy - 1), abs(dx) + abs(dy), dx, dy)
            best_pref = (abs(best_move[0] - 1) + abs(best_move[1] - 1), abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])
            if pref < best_pref:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]