def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal-friendly)

    mypos = (sx, sy)
    opp = (ox, oy)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))

    if not resources:
        # No resources: drift toward center to reduce worst-case time
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            if bestd is None or d < bestd:
                bestd, best = d, (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose a target we can realistically reach no later than the opponent
    # Prefer resources that we are closer to in Chebyshev distance.
    best_targets = []
    for t in resources:
        md = dist(mypos, t)
        od = dist(opp, t)
        # primary: we want md - od as small as possible (prefer winning races)
        # secondary: md smaller
        key = (md - od, md, t[0], t[1])
        best_targets.append((key, t))
    best_targets.sort()
    # consider top few deterministically
    candidates = [t for _, t in best_targets[:min(5, len(best_targets))]]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        score = 0
        myn = (nx, ny)
        # Evaluate against best candidate resource race
        for t in candidates:
            md = dist(myn, t)
            od = dist(opp, t)
            # reward reaching resources; reward winning races; penalize letting opponent win
            score += (30 - md) + (8 if md <= od else -12) + (3 if md + 1 <= od else 0)
        # Obstacle avoidance already handled; add mild anti-stagnation
        score -= (0 if (dx == 0 and dy == 0) else 0)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]