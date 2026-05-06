def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # If no resources, just drift toward center-ish while avoiding edges (deterministic).
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = king_dist(nx, ny, tx, ty)
            key = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    opp_close_now = king_dist(sx, sy, ox, oy) <= 2
    rem = observation.get("remaining_resource_count", len(resources))
    center_bias = 0.03 * (rem >= 6)

    # Evaluate best move by considering best target resource after the move.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in valid:
        move_score = None
        # Deterministic scan order fallback
        for rx, ry in resources:
            ds = king_dist(nx, ny, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            adv = do - ds  # higher is better (we are closer)
            # If opponent can grab next, strongly discourage
            opp_threat = 6.0 if do <= 1 else (2.5 if do == 2 else 0.0)
            # Encourage finishing: smaller ds is better
            finish = 1.2 / (1 + ds)
            # Slight preference for moving along our advantage direction, plus stability
            dist_to_our_target = (ds <= 1) * 0.8 + (ds == 0) * 1.2
            # Center bias to avoid corner-lock if ties
            cb = center_bias * (king_dist(nx, ny, w // 2, h // 2) * -1)
            # When opponent is near us, weight threats more
            danger_weight = 1.6 if opp_close_now else 1.0
            score = adv * 2.0 + finish + dist_to_our_target + cb - opp_threat * danger_weight
            key = (-score, ds, do, rx, ry)  # minimize lexicographically
            if move_score is None or key < move_score[0]:
                move_score = (key, score)
        if move_score is None:
            continue
        if best_key is None or move_score[0] < best_key:
            best_key = move_score[0]
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]