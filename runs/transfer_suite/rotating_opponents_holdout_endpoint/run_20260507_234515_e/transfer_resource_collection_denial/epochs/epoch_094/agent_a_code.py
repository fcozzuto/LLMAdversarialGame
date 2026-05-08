def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    # One-step "race" heuristic: choose move that creates the best advantage over opponent
    # for the best reachable resource after this move.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Score by the best (our_distance, opponent_distance) margin across resources.
        # Larger advantage is better; slight preference for nearer resources.
        local_best = -10**18
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # If we can arrive strictly sooner, that's strong; if tied/behind, it's weak.
            margin = d_opp - d_me
            val = margin * 10 - d_me
            # Mild tie-break: avoid giving the opponent a faster or equal path when very close.
            if margin <= 0 and d_me <= 2:
                val -= 30
            if val > local_best:
                local_best = val

        # Secondary tie-break: stay away from obstacles is already ensured; use opponent proximity to avoid "shadow blocking".
        opp_prox_pen = -man(nx, ny, ox, oy)
        score = local_best + opp_prox_pen * 0.1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]