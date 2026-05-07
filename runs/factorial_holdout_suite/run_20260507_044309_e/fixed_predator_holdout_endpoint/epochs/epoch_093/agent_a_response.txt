def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    turns_remaining = int(observation.get("turns_remaining") or 0)
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Win potential: prioritize targets we can reach no later than opponent.
        win_margin = (od - sd)
        # Slight urgency: earlier reach and having time to collect.
        urgency = turns_remaining - sd
        key = (win_margin, urgency, -sd, -od, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move choice: consider 9 possible deltas; score by progress to target and denial defense.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        self_d = man(nx, ny, tx, ty)
        # Deny: if opponent is closer to the chosen target, reduce their lead; else just push.
        opp_d = man(ox, oy, tx, ty)
        # Also discourage stepping near obstacles.
        near_obs = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + adx, ny + ady
            if (ax, ay) in obstacles:
                near_obs += 1
        # Tie-break deterministically by preferring moves that keep direction and reduce distance.
        key = ((opp_d - self_d), -self_d, -near_obs, dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]