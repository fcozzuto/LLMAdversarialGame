def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()

    we_evade = ("evader" in self_role) or ("evade" in self_role) or (("pursuer" in opp_role) and ("evader" in self_role or "evade" in self_role))
    # If roles are ambiguous, infer by opponent role.
    if ("pursuer" in self_role) and ("evader" in opp_role):
        we_evade = False
    if ("evader" in self_role) and ("pursuer" in opp_role):
        we_evade = True
    if "pursuer" in self_role and "evader" not in opp_role and "evade" not in self_role:
        we_evade = False

    best = None
    best_move = [0, 0]
    # Deterministic move order: prioritize straight then diagonal, and prefer earlier axes.
    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Simple obstacle proximity penalty to avoid hugging walls/blocks.
        prox = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in obs:
                prox += 1

        center_bias = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        if we_evade:
            # Maximize distance; reduce proximity to obstacles; keep some centering to avoid corner traps.
            key = (d2, -prox, -center_bias)
        else:
            # Minimize distance; reduce proximity; also avoid wasting moves by centering slightly.
            key = (-d2, -prox, center_bias)

        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]