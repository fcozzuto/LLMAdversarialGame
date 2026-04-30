def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((p[0], p[1]))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        best = None
        bestv = -10**9
        for rx, ry in resources:
            d1 = manh(sx, sy, rx, ry)
            d2 = manh(ox, oy, rx, ry)
            v = (d2 - d1) * 2 - d1  # prefer resources we can reach sooner than opponent
            # slight bias toward nearer absolute targets
            v -= 0.1 * (d1 + d2)
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        our_d = manh(nx, ny, tx, ty)
        opp_d = manh(nx, ny, ox, oy)
        curr_our_d = manh(sx, sy, tx, ty)
        curr_opp_d = manh(sx, sy, ox, oy)

        # primary: go toward target
        score = -our_d * 3
        # secondary: don't let opponent get closer to us while we chase
        score += (opp_d - curr_opp_d) * 0.7
        # tertiary: if we can reach target next, prefer it
        score += 50 if our_d == 0 else 0
        # keep movement meaningful
        score += 0.2 * (curr_our_d - our_d)
        # avoid stepping into dead simple mirror when targeting same resource
        if resources and manh(ox, oy, tx, ty) <= manh(sx, sy, tx, ty) and dx == 0 and dy == 0:
            score -= 1.5

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]