def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    if not resources:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    best_move = moves[0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        cur_best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # Collecting now gets huge value; otherwise prioritize becoming/remaining earlier than opponent.
            val = (5000 if sd == 0 else 0) + (120 * adv) - (3 * sd)
            if val > cur_best:
                cur_best = val
        # Small deterministic tie-break: prefer staying close to current best resource direction
        tie = -man(nx, ny, ox, oy)
        score = cur_best + 0.01 * tie
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]