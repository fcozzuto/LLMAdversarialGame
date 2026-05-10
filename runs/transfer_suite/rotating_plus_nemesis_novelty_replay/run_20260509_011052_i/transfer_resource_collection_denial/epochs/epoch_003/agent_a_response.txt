def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    resources = observation.get("resources", []) or []
    if not resources:
        # drift toward center, but prefer moving away from edges deterministically
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx if (sx + dx, sy + 0) not in obs else 0, dy if (sx + 0, sy + dy) not in obs else 0]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource we can beat (positive margin). If none, pick one where we minimize being beaten.
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        margin = opd - myd  # positive means we are closer
        key = (-(margin), myd, rx, ry)  # minimize -margin => maximize margin
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Choose move that maximizes (oppdist - mydist) after the move, then minimizes mydist, then deterministic tie.
    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd2 = abs(tx - nx) + abs(ty - ny)
        opd2 = abs(tx - ox) + abs(ty - oy)
        margin2 = opd2 - myd2
        # Primary: maximize margin2; Secondary: minimize myd2; Tertiary: prefer toward target; Quaternary: deterministic by dx,dy.
        toward = (abs(tx - nx) + abs(ty - (ny))) - (abs(tx - sx) + abs(ty - sy))
        score = ( -margin2, myd2, toward, dx, dy )
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]