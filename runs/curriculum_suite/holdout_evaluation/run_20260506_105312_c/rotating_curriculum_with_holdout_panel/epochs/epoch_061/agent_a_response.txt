def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist(nx, ny, tx, ty)
            k = (d, dist(nx, ny, ox, oy), nx, ny)
            if k < (best[0], best[1], best[2], best[3]):
                best = (d, dist(nx, ny, ox, oy), dx, dy)
        return [best[2], best[3]]

    # Pick a target that we can reach sooner, but strongly punish resources that opponent is already closer to.
    # Small deterministic bias toward cells that reduce our distance and increase opponent distance.
    best_target = None
    best_key = (10**9, 10**9, 10**9)
    for rx, ry in resources:
        dS = dist(sx, sy, rx, ry)
        dO = dist(ox, oy, rx, ry)
        if dS == 0:
            key = (-10**6, 0, dO)
        else:
            lead = dO - dS  # positive if we are closer
            # Penalize letting opponent be closer; reward being closer and closer faster.
            key = (-lead, dS, dO)
        if key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (10**9, 10**9, 0, 0)
    # Greedy step toward chosen target, with obstacle avoidance and secondary goal: widen gap vs opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dS2 = dist(nx, ny, tx, ty)
        dO2 = dist(nx, ny, ox, oy)
        # Primary: minimize distance to target; Secondary: maximize opponent distance; Tertiary: deterministic ordering by position.
        k = (dS2, -dO2, nx, ny)
        if k < (best_move[0], best_move[1], best_move[2], best_move[3]):
            best_move = (dS2, -dO2, dx, dy)

    return [best_move[2], best_move[3]]