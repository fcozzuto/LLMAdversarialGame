def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Prefer resources where we are closer; discourage letting opponent be closer.
            score = (opd - myd) * 10 - myd
            # Encourage collecting sooner if opponent is generally far.
            score += (0 if observation.get("turns_remaining") is None else int(observation["turns_remaining"] > 0)) * (opd - myd >= 0)
            key = (score, -myd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        _, rx, ry = best
        target_myd = man(sx, sy, rx, ry)
    else:
        # No visible resources: move to a center-ish cell, biased away from opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        rx, ry = cx, cy
        target_myd = man(sx, sy, rx, ry)

    best_move = None
    for dx, dy, nx, ny in valid_moves:
        d_next = man(nx, ny, rx, ry)
        # If we can reach in 1 step, prioritize.
        reach_bonus = 30 if d_next <= 1 else 0
        # Slightly prefer increasing opponent distance.
        opp_d_before = man(ox, oy, rx, ry)
        opp_d_after = man(ox, oy, rx, ry)
        opp_bonus = 0
        # Tie-breaking only: favor smaller distance; slight preference to move toward target.
        score = -d_next + reach_bonus + opp_bonus + (1 if d_next < target_myd else 0) * 0.1
        key = (score, -man(nx, ny, ox, oy), -nx, -ny, -abs(dx), -abs(dy))
        if best_move is None or key > best_move[0]:
            best_move = (key, dx, dy)

    return [int(best_move[1]), int(best_move[2])]