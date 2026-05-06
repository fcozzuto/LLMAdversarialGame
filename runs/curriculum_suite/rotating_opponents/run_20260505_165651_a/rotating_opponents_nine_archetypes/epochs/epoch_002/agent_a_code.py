def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set(tuple(r) for r in resources)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    # Pick a target resource that we are relatively closer to (deterministic: sort key)
    ranked = sorted(resources, key=lambda r: (-(cheb(x, y, r[0], r[1]) - cheb(ox, oy, r[0], r[1])) , r[0], r[1]))
    targets = ranked[:4]  # small deterministic set

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        on_res = 1 if (nx, ny) in res_set else 0
        # Prefer moves that secure a good target while not giving opponent advantage
        score = on_res * 1000
        for rx, ry in targets:
            our = cheb(nx, ny, rx, ry)
            opp = cheb(ox, oy, rx, ry)
            # If we are closer/equal, encourage. If opponent is much closer, discourage.
            score += (opp - our) * 50
            # Mild distance-to-target tie-breaker
            score += (10 - our) * 2

        # Obstacle/edge safety: prefer staying within board and not moving adjacent into obstacles
        adj_pen = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                ax1, ay1 = nx + ex, ny + ey
                if ax1 < 0 or ax1 >= w or ay1 < 0 or ay1 >= h:
                    adj_pen += 1
                elif (ax1, ay1) in obstacles:
                    adj_pen += 3
        score -= adj_pen

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]