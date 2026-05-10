def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Select a target we can reach earlier than opponent (or at least contest strongly),
    # with a slight bias for nearer resources.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        lead = do - ds  # >0 means we are closer
        # Prefer resources aligned with "approach corridor" away from opponent:
        # if resource is on the side opponent is farther from, it tends to be safer.
        side_bias = 0
        if (rx - ox) * (rx - sx) < 0:
            side_bias = 0.3
        # Strongly prefer immediate contest wins
        key = (-lead - side_bias * 0.5, ds + 0.05 * abs(ry - oy), rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), lead, ds)
    tx, ty = best[1]

    # Pick the move that minimizes distance to chosen target,
    # while avoiding stepping into obstacles and discouraging giving opponent a lead.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = abs(tx - nx) + abs(ty - ny)
        # If we could become less competitive, penalize.
        nds = myd
        ndo = abs(tx - ox) + abs(ty - oy)
        mylead_next = ndo - nds
        # Small preference to avoid moving toward opponent position.
        opp_close = abs(nx - ox) + abs(ny - oy)
        cur_opp_close = abs(sx - ox) + abs(sy - oy)
        opp_pen = (opp_close - cur_opp_close) * 0.05
        key = (myd + (0 if mylead_next >= 0 else 2.0), -mylead_next, opp_pen, dx, dy)
        if best_move[0] is None or key < best_move[0]:
            best_move = (key, [dx, dy])

    return best_move[1]