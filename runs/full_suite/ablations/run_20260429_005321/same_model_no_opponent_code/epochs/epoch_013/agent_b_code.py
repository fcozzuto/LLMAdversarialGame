def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Pick a target resource that is relatively closer to us and farther from opponent.
    tx, ty = x, y
    if resources:
        best = None
        for rx, ry in resources:
            # lower is better
            score = d2(rx, ry, x, y) - (0.9 * d2(rx, ry, ox, oy))
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    # If resources are empty, head away from opponent to preserve survival/deny.
    if not resources:
        tx, ty = (0 if ox > x else w - 1), (0 if oy > y else h - 1)

    best_move = (0, 0)
    best_val = -10**30

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Main: move closer to chosen target.
        base = -d2(nx, ny, tx, ty)

        # Collision/obstacle avoidance: strong penalty near obstacles, reward for clearing.
        obs_pen = 0
        for px, py in obstacles:
            dd = d2(nx, ny, px, py)
            if dd == 0:
                obs_pen += 10**9
            elif dd == 1:
                obs_pen += 400
            elif dd == 2:
                obs_pen += 220
            elif dd <= 8:
                obs_pen += 80
        # Avoid stepping onto/adjacent to opponent unless it also improves target distance a lot.
        opp_pen = 0
        opp_d = d2(nx, ny, ox, oy)
        if opp_d == 0:
            opp_pen += 10**7
        elif opp_d <= 2:
            opp_pen += 600
        elif opp_d <= 8:
            opp_pen += 140

        # Prefer moves that improve target progress relative to staying still.
        prog = d2(x, y, tx, ty) - d2(nx, ny, tx, ty)

        val = base + (8 * prog) - obs_pen - opp_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]