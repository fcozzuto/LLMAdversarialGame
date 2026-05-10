def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)

    obs_set = set((x, y) for x, y in obstacles)
    if not resources:
        return [0, 0]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= grid_w: nx = grid_w - 1
        if ny >= grid_h: ny = grid_h - 1
        return nx, ny

    # Pick best resource by advantage: (opp_dist - self_dist) descending, then smaller self_dist, then coords
    best = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (od - sd, -sd, -rx, -ry)  # higher advantage first
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Evaluate one-step move: maximize (opponent distance - our distance) at next, prefer closer to target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obs_set:
            continue
        myd = abs(tx - nx) + abs(ty - ny)
        oppd = abs(tx - nx) + abs(ty - ny)
        # Lead at next step relative to opponent: how much better we are getting vs opponent on this target
        lead_n = (abs(tx - ox) + abs(ty - oy)) - myd
        lead_now = (abs(tx - ox) + abs(ty - oy)) - (abs(tx - sx) + abs(ty - sy))
        progress = lead_n - lead_now
        # Secondary: reduce own distance and move toward target
        tx_dist = myd
        val = progress * 100 - tx_dist * 3 + (1 if (nx, ny) == (tx, ty) else 0) * 10000 + (0 if (nx, ny) == (sx, sy) else 1)
        # Slightly deny opponent by pushing them farther from our target (target is fixed)
        opp_dist_now = abs(tx - ox) + abs(ty - oy)
        val += (opp_dist_now - oppd) * 0  # keep deterministic, neutral
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves hit obstacles, stay
    return [int(best_move[0]), int(best_move[1])]