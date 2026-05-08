def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # If no resources, drift toward center
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            score = -manh(nx, ny, tx, ty)
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate best resource from the hypothetical new position
        # Primary: how much sooner we can arrive vs opponent; Secondary: closer arrival; Tertiary: tie by coords.
        local_best = None
        for rx, ry in resources:
            d_ours = manh(nx, ny, rx, ry)
            d_opp = manh(ox, oy, rx, ry)
            adv = d_opp - d_ours  # positive means we are sooner
            dist_pen = d_ours
            # Discrete scoring to stay deterministic
            score = adv * 100 - dist_pen
            key = (score, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key
        if local_best is None:
            continue
        final_score = local_best[0]

        if best_score is None or final_score > best_score or (final_score == best_score and (dx, dy) < best_move):
            best_score = final_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]