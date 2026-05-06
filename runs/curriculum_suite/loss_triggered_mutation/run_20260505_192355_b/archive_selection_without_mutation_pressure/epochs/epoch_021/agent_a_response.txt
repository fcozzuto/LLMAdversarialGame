def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def lex_better(a, b):
        return a > b

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    # Estimate opponent's likely target: closest resource to opponent now.
    # Then prefer our move that increases that resource distance or reduces our distance to it.
    opp_target = None
    opp_best_od = 10**9
    for rx, ry in resources:
        od = dist(ox, oy, rx, ry)
        if od < opp_best_od:
            opp_best_od = od
            opp_target = (rx, ry)

    # Secondary objective: overall best "advantage" (opp_d - self_d) against any resource.
    best_move = [0, 0]
    best_key = (-10**18, -10**18, -10**18, -10**18)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            # Find best advantage over all resources after our move.
            max_gap = -10**18
            min_self_d = 10**18
            min_opp_d = 10**18
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                gap = od - sd
                if gap > max_gap:
                    max_gap = gap
                if sd < min_self_d:
                    min_self_d = sd
                if od < min_opp_d:
                    min_opp_d = od

            # Choke heuristic around estimated opponent target.
            # We cannot control opponent directly, but moving closer to their target reduces
            # their relative advantage; moving away increases their competitiveness elsewhere.
            if opp_target is not None:
                tx, ty = opp_target
                opp_target_sd = dist(nx, ny, tx, ty)
                opp_target_od = dist(ox, oy, tx, ty)
                choke_gap = opp_target_od - opp_target_sd  # higher => we are closer
            else:
                choke_gap = max_gap

            # Prefer moves that keep us centered a bit (prevents corner traps) when tied.
            center_pen = abs(nx - cx) + abs(ny - cy)

            # Key: maximize max_gap, then maximize choke_gap, then minimize min_self_d and center_pen.
            key = (max_gap, choke_gap, -min_self_d, -center_pen)
            if lex_better(key, best_key):
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]