def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources", []) or []
    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))
    if w <= 0 or h <= 0:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    turn = int(observation.get("turn_index", 0) or 0)

    if resources:
        # Alternate between "chase" and "kite" to improve robustness vs diagonal probes.
        kite_mode = (turn % 4 == 1 or turn % 4 == 2)
        rx0, ry0 = None, None
        bestd = 10**18
        # Deterministically pick a promising resource: prefer those not near obstacles (simple penalty).
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            d = abs(sx - rx) + abs(sy - ry)
            if d < bestd:
                bestd = d
                rx0, ry0 = rx, ry
        if rx0 is None:
            rx0, ry0 = int(resources[0][0]), int(resources[0][1])
    else:
        rx0, ry0 = ox, oy  # fallback

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        # Resource pressure: prefer moving toward chosen resource.
        dres = abs(nx - rx0) + abs(ny - ry0) if resources else 0

        # Opponent pressure: avoid being diagonally "tapped" by keeping distance or steering to alter parity.
        dop = abs(nx - ox) + abs(ny - oy)
        # Encourage a parity change every other step to disrupt diagonal alignment.
        parity_now = (sx + sy) & 1
        parity_next = (nx + ny) & 1
        parity_bonus = 1 if parity_next != parity_now else 0

        # If kite_mode, weight opponent distance more; else weight resource more.
        if resources:
            if kite_mode:
                val = (dop * 12) + (parity_bonus * 3) - (dres * 3)
            else:
                val = (dop * 4) + (parity_bonus * 2) - (dres * 9)
        else:
            val = dop + parity_bonus

        # Mild tie-breaker toward reducing Manhattan distance to opponent's direction.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]