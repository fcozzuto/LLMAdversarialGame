def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # Precompute opponent distances to each resource
    opp_d = {}
    for rx, ry in res:
        opp_d[(rx, ry)] = md(ox, oy, rx, ry)

    best_move = None
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = 0

        if (nx, ny) in opp_d:
            score += 10000  # immediate pickup

        # Aim: resources we are closer to than opponent; also prioritize closeness overall.
        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            d_op = opp_d[(rx, ry)]
            if d_self == 0:
                continue

            # Gain if we can be the first/closer pursuer for this resource
            rel = d_op - d_self  # positive means we are closer
            if rel > 0:
                score += 50 * rel / (1 + d_self)  # stronger when close
            else:
                # mild preference for overall closeness to remaining resources
                score += 2 / (1 + d_self)

        # Anti-jitter: prefer moves that reduce distance to our best target
        # Define best target as resource maximizing (opp_d - dist from current)
        cur_best_rel = None
        for rx, ry in res:
            rel0 = opp_d[(rx, ry)] - md(sx, sy, rx, ry)
            if cur_best_rel is None or rel0 > cur_best_rel:
                cur_best_rel = rel0
        score += cur_best_rel * 0.1

        # Tie-break deterministically by small preference to cardinal over diagonal, then lexicographic
        diag = 1 if dx != 0 and dy != 0 else 0
        score -= diag * 0.01
        score -= (dy + 1) * 0.0001 + (dx + 1) * 0.00001

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]