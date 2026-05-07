def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [0, 0]

    # Pick a target resource: maximize advantage, then centrality, then "opponent blocked next"
    best = None
    cx, cy = w // 2, h // 2
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Opponent greedy next step toward this resource (Chebyshev step).
        step_x = 0 if rx == ox else (1 if rx > ox else -1)
        step_y = 0 if ry == oy else (1 if ry > oy else -1)
        nx, ny = ox + step_x, oy + step_y
        opp_blocked = (nx < 0 or nx >= w or ny < 0 or ny >= h) or ((nx, ny) in obstacles)
        center = -cheb(rx, ry, cx, cy)  # closer to center is better
        # Advantage-first; discourages giving opponent a nearer race.
        score = (do - ds) * 10.0 + (1.0 if opp_blocked else 0.0) * 3.0 + center * 0.5
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best

    # Choose one move: among legal moves, minimize distance to target; break ties by maximizing opponent distance.
    best_move = (None, -10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)  # opponent unchanged this turn
        center2 = -cheb(nx, ny, cx, cy)
        # Primary: smaller ds2. Secondary: larger center2. Tertiary: larger (do2 - ds2).
        adv2 = do2 - ds2
        key = (-ds2, -center2, -adv2, dx, dy)
        if best_move[0] is None or key < best_move[0]:
            best_move = (key, 0, [dx, dy])

    if best_move[2] is None:
        return [0, 0]
    return best_move[2]