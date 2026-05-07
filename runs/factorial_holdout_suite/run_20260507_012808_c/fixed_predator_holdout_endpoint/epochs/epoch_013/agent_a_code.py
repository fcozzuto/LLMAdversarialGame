def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            self_d = abs(nx - tx) + abs(ny - ty)
            opp_d = abs(nx - ox) + abs(ny - oy)
            v = (opp_d - self_d)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource that we are most ahead of (or least behind).
    best_res = None
    best_res_score = -10**18
    for rx, ry in resources:
        self_d = dist(sx, sy, rx, ry)
        opp_d = dist(ox, oy, rx, ry)
        # Primary: maximize (opp_d - self_d). Secondary: prefer smaller self_d.
        score = (opp_d - self_d) * 1000 - self_d
        if score > best_res_score:
            best_res_score = score
            best_res = (rx, ry)

    rx, ry = best_res
    # Choose move that best improves our access to the target while avoiding losing the race.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        self_to = dist(nx, ny, rx, ry)
        opp_to = dist(ox, oy, rx, ry)
        # If opponent is already closer, we try to reduce the gap faster.
        gap = opp_to - self_to
        cur_gap = dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry)
        # Also lightly prefer moves that decrease our distance to the target even when tied.
        val = gap * 1000 + (cur_gap - gap) * 10 - self_to
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]