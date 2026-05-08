def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cd(ax, ay, bx, by):
        a = ax - bx
        b = ay - by
        if a < 0:
            a = -a
        if b < 0:
            b = -b
        return a if a >= b else b

    # If no visible resources, move to slightly improve position (toward center).
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dist = abs(nx - cx) + abs(ny - cy)
            key = (dist, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move that maximizes our advantage to a resource (opp_distance - self_distance).
    # Prefer larger advantage, then smaller self distance, then lexicographic move.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        move_best = None
        move_best_key = None
        for rx, ry in resources:
            self_d = cd(nx, ny, rx, ry)
            opp_d = cd(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive => likely take before opponent
            # Small penalty if we step further from current local best; keeps action stable.
            key = (-adv, self_d, rx, ry)  # use -adv for minimization
            if move_best_key is None or key < move_best_key:
                move_best_key = key
                move_best = adv
        # Overall key for the move: maximize adv, then minimize self_d, then lexicographic.
        # Recover adv from move_best_key.
        adv = move_best
        self_d = move_best_key[1]
        key = (-adv, self_d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]