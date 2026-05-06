def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If no visible resources, try to drift toward center to avoid being static
    if not res:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            key = (md(nx, ny, cx, cy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Precompute per-resource reach times (by Manhattan distance)
    # Use a deterministic tie-break by coordinates.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Prefer moves that create a large advantage on some resource,
        # while discouraging resources where the opponent is already closer.
        own_best = None
        opp_best = None
        for rx, ry in res:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # advantage > 0 means we are closer than opponent (good capture)
            adv = do - ds
            # side preference: closer to our corner direction (0,0-ish vs opposite corner-ish)
            side = md(nx, ny, 0, 0) if (sx + sy) <= (w - 1 - sx + h - 1 - sy) else md(nx, ny, w - 1, h - 1)
            # Opponent threat: resources where opponent is much closer
            threat = ds - do
            key_own = (-adv, side, rx, ry)
            key_opp = (threat, rx, ry)
            if own_best is None or key_own < own_best[0]:
                own_best = (key_own, adv, rx, ry)
            if opp_best is None or key_opp < opp_best[0]:
                opp_best = (key_opp, threat, rx, ry)

        # Final move score: maximize advantage, minimize giving opponent "easy" captures.
        # Also slight penalty for staying too close to opponent (avoid being shadowed).
        adv = own_best[1]
        threat = opp_best[1]
        dist_to_opp = md(nx, ny, ox, oy)
        # Deterministic composite key: higher adv, lower threat, higher separation, then dx/dy
        key = (-adv, threat, -dist_to_opp, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]] if best_move else [0, 0]