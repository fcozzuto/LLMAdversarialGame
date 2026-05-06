def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # If no resources, position defensively (stay away from opponent, avoid edges if possible)
    if not resources:
        best_move = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = abs(nx - ox) + abs(ny - oy)
            edge_pen = (0 if 1 <= nx < w - 1 and 1 <= ny < h - 1 else 2)
            key = (-d_opp, edge_pen, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    # Choose a target resource where we are relatively closer than opponent, biased toward controlling mid-game routes.
    best_target = None
    best_tkey = None
    for rx, ry in resources:
        ds = abs(sx - rx) + abs(sy - ry)
        do = abs(ox - rx) + abs(oy - ry)
        # Prefer resources where we have advantage; also prefer not-too-far targets.
        adv = do - ds  # positive => we are closer
        # Mid bias: prefer resources not stuck in corners too heavily.
        mid_bias = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        tkey = (-adv, ds, mid_bias, rx, ry)
        if best_tkey is None or tkey < best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    rx, ry = best_target
    # If opponent is immediately adjacent, disrupt by moving to reduce their ability to step onto target next.
    # Otherwise greedy step toward target with obstacle-aware and opponent-repulsion.
    opp_close = (abs(sx - ox) <= 1 and abs(sy - oy) <= 1)

    best_move = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = abs(nx - rx) + abs(ny - ry)
        do_next = abs(nx - ox) + abs(ny - oy)

        # Disruption: if opponent close, prioritize increasing opponent distance and also preventing direct convergence to target.
        disrupt = 0
        if opp_close:
            opp_to_target = abs(ox - rx) + abs(oy - ry)
            disrupt = (0.7 * (-do_next)) + (0.5 * (ds_next))  # lower is better via key

        # General scoring: reduce distance to target, but avoid moving closer to opponent too much.
        opp_weight = 1.2 if ds_next <= 2 else 0.6
        opp_pen = opp_weight * (10 - do_next)  # higher do_next reduces penalty

        edge_pen = 0 if 0 < nx < w - 1 and 0 < ny < h - 1 else 1
        # Key: minimize combined objective deterministically.
        mkey = (ds_next, edge_pen, opp_pen, disrupt, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    return best_move