def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2 and (r[0], r[1]) not in obs:
            resources.append((r[0], r[1]))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If no resources, move to reduce distance to opponent's side deterministically
    if not resources:
        tx, ty = (w - 1, h - 1) if ox < w // 2 else (0, 0)
        best = None
        for dx, dy, nx, ny in moves:
            key = (dist(nx, ny, tx, ty), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    dirs = [(dx, dy, nx, ny) for (dx, dy, nx, ny) in moves]
    best_key = None
    best_move = (0, 0)

    for dx, dy, nx, ny in dirs:
        # Evaluate the best resource for us, with opponent contention.
        best_adv = None
        best_us_d = None
        for rx, ry in resources:
            us = dist(nx, ny, rx, ry)
            opp = dist(ox, oy, rx, ry)
            # Advantage: favor being closer than opponent; strongly penalize giving opponent the win.
            adv = (opp - us)
            if best_adv is None or (adv, -us, -rx, -ry) > (best_adv, -best_us_d, -best_rx, -best_ry):
                best_adv = adv
                best_us_d = us
                best_rx, best_ry = rx, ry

        # Primary: maximize advantage; Secondary: minimize our distance; Tertiary: deterministic tie-break
        # Also encourage moving toward resources even if no strict advantage.
        us_d = best_us_d
        key = (-best_adv, us_d, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]