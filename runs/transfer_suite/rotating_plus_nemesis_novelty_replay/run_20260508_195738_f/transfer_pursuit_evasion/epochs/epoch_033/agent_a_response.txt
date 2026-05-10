def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    is_evader = (str(observation.get("self_role", "")).lower() == "evader")

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_move = [0, 0]
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        corner_d = 0
        for cx, cy in corners:
            cd = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            if cd > corner_d:
                corner_d = cd

        # obstacle proximity penalty to avoid getting stuck in zig-zag lanes
        prox = 0
        for tx in (nx - 1, nx, nx + 1):
            for ty in (ny - 1, ny, ny + 1):
                if (tx, ty) in obs:
                    prox += 1

        # Deterministic tie-breaker by slight bias toward reducing/expanding d2.
        if is_evader:
            sc = d2 * 10 + corner_d * 0.0005 - prox * 1.5
            better = (best_sc is None) or (sc > best_sc)
        else:
            sc = -d2 * 10 + corner_d * 0.0005 - prox * 1.5
            better = (best_sc is None) or (sc > best_sc)

        if better:
            best_sc = sc
            best_move = [dx, dy]

    return best_move