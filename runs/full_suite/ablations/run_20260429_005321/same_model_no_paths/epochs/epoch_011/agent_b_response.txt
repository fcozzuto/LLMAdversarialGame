def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def obs_pen(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    # Pick a target resource where we have (or can create) advantage in reachability.
    target = None
    best_adv = -10**18
    if resources:
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            # Slightly prefer nearer resources overall to reduce dithering.
            adv2 = adv * 10 - (ds + do)
            if adv2 > best_adv:
                best_adv = adv2
                target = (rx, ry)

    # If no resources, drift to a corner opposite opponent.
    if not target:
        tx, ty = (0, 0) if (ox > w // 2 or oy > h // 2) else (w - 1, h - 1)
        dxs, dys = tx - sx, ty - sy
        sx1 = sx + (1 if dxs > 0 else -1 if dxs < 0 else 0)
        sy1 = sy + (1 if dys > 0 else -1 if dys < 0 else 0)
        if valid(sx1, sy1):
            return [sx1 - sx, sy1 - sy]
        return [0, 0]

    tx, ty = target

    # Evaluate each move by (1) our progress to target, (2) denial: how close opponent gets next step,
    # (3) obstacle proximity.
    def best_opponent_next_dist_to_target():
        best = 10**9
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < best:
                best = d
        return best if best != 10**9 else man(ox, oy, tx, ty)

    opp_best_now = best_opponent_next_dist_to_target()

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        # If we land adjacent/at target, strongly prefer.
        reach_bonus = 30 if d_self == 0 else 10 if d_self == 1 else 0
        # Denial term: if we get closer than opponent is, reward; else mildly punish.
        d_opp_now = opp_best_now
        advantage = d_opp_now - d_self
        # Also discourage stepping into obstacle-dense areas.
        pen = obs_pen(nx, ny)
        # Prefer positions that reduce our distance more than they reduce opponent's.
        score = advantage * 12 - d_self * 3 + reach_bonus - pen * 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]